import urllib.request
import urllib.parse
import re
from datetime import datetime

class BlogStyleLearner:
    """
    [내 블로그 링크 자동 학습 & 긍정적 스타일 진화 엔진]
    - 사용자가 실제로 업로드한 네이버 블로그 링크를 입력받아 분석
    - 글쓴이의 고유 말투(경어체/구어체), 문장 길이, 자주 쓰는 어미, 첫인사/끝인사 시그니처 감지
    - 다음 글 생성부터 해당 블로그의 색깔에 맞춰 100% 자동 업그레이드 반영
    """

    @classmethod
    def analyze_published_blog(cls, blog_url: str) -> dict:
        blog_url = (blog_url or "").strip()
        if not blog_url.startswith("http"):
            raise ValueError("올바른 블로그 URL을 입력해 주세요.")

        # 네이버 블로그 URL을 모바일 뷰로 변환하여 본문 텍스트 직접 추출
        target_url = blog_url
        if "blog.naver.com" in blog_url and "m.blog.naver.com" not in blog_url:
            target_url = blog_url.replace("blog.naver.com", "m.blog.naver.com")

        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
        }

        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            # 접속 실패 시 더 일반적인 헤더로 재시도
            try:
                headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                req = urllib.request.Request(target_url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
            except Exception as e2:
                raise RuntimeError(f"블로그 페이지를 읽어올 수 없습니다: {str(e2)}")

        # 본문 텍스트 추출 (네이버 스마트에디터 ONE 컨테이너 또는 일반 텍스트)
        clean_text = ""
        # 1. 스마트에디터 ONE 문단 수집
        paragraphs = re.findall(r'<p[^>]*class="[^"]*se-text-paragraph[^"]*"[^>]*>(.*?)</p>', html, flags=re.DOTALL)
        if paragraphs:
            for p in paragraphs:
                pt = re.sub(r'<[^>]+>', ' ', p).strip()
                if pt:
                    clean_text += pt + "\n"
        
        # 2. 없으면 일반 body에서 태그 제거
        if len(clean_text) < 100:
            body = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
            body = re.sub(r'<style.*?</style>', '', body, flags=re.DOTALL)
            body = re.sub(r'<[^>]+>', ' ', body)
            clean_text = re.sub(r'\s+', ' ', body)

        if len(clean_text) < 50:
            raise ValueError("블로그 본문 텍스트가 너무 짧거나 비공개 글입니다. 공개된 블로그 포스팅 링크를 입력해 주세요.")

        # ====================================================
        # 블로거 고유 스타일 심층 분석
        # ====================================================
        lines = [line.strip() for line in clean_text.split('\n') if len(line.strip()) > 5]
        
        # 1. 어투 분석 (존댓말/경어체 vs 털털한 구어체/반말)
        polite_markers = ["습니다", "해요", "답니다", "세요", "네요", "드립니다", "있어요", "보세요", "같아요"]
        casual_markers = ["했음", "함", "ㅋㅋ", "ㅎㅎ", "임", "더라고요", "존맛", "개편함", "쌉가능", "ㄷㄷ"]

        polite_count = sum(clean_text.count(m) for m in polite_markers)
        casual_count = sum(clean_text.count(m) for m in casual_markers)

        if polite_count >= casual_count:
            dominant_tone = "polite"
            tone_name = "다정하고 따뜻한 이웃 소통형 경어체 ('~해요', '~답니다')"
        else:
            dominant_tone = "casual"
            tone_name = "솔직 담백하고 털털한 찐후기 구어체 ('~했음', '~하더라고요')"

        # 2. 첫인사 시그니처 감지
        first_greeting = ""
        for line in lines[:5]:
            if any(w in line for w in ["안녕", "반갑", "이웃", "날씨", "오늘", "환영"]):
                first_greeting = line[:60]
                break
        if not first_greeting and lines:
            first_greeting = lines[0][:60]

        # 3. 끝인사 시그니처 감지
        closing_phrase = ""
        for line in reversed(lines[-7:]):
            if any(w in line for w in ["감사", "공감", "댓글", "이웃", "소통", "행복", "도움", "좋아요"]):
                closing_phrase = line[:60]
                break

        # 4. 이모지/이모티콘 사용 빈도
        emoji_count = len(re.findall(r'[\U00010000-\U0010ffff]|[\u2600-\u27ff]|(?:[~!?]{2,})|(?:[ㅋㅎ]{2,})', clean_text))
        emoji_preference = "high" if emoji_count > 15 else "normal"

        profile = {
            "blog_url": blog_url,
            "tone_key": dominant_tone,
            "tone_name": tone_name,
            "first_greeting": first_greeting or "안녕하세요! 오늘도 유용한 꿀팁 전해드리러 왔습니다 :)",
            "closing_phrase": closing_phrase or "오늘 포스팅이 도움 되셨다면 공감과 따뜻한 댓글 부탁드려요 💕",
            "emoji_preference": emoji_preference,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return profile
