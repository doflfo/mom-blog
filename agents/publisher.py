import json
import urllib.request
import urllib.parse
import base64
from core.database import get_settings

class PublisherAgent:
    """
    [직원 4: 총괄 퍼블리셔 & 플랫폼 배포자 '도현']
    - 역할: 최종 승인된 고품질 콘텐츠를 블로그 및 쓰레드 등 멀티 플랫폼으로 자동 업로드
    - 지원 플랫폼:
      ① 워드프레스 (WordPress REST API 자동 포스팅)
      ② 티스토리 (Tistory Open API)
      ③ 네이버 블로그 (원클릭 스마트에디터 서식 복사 및 자동화 템플릿)
      ④ Threads (타래별 분할 텍스트 포맷팅 및 메타 API 규격 지원)
    """
    def __init__(self):
        self.name = "도현 (총괄 퍼블리셔)"
        self.role = "Platform Operations & Publisher"

    def publish_to_wordpress(self, title: str, content_html: str, status="draft") -> dict:
        """워드프레스 REST API로 자동 포스팅"""
        settings = get_settings()
        wp_url = settings.get("wp_site_url", "").strip().rstrip("/")
        wp_user = settings.get("wp_username", "").strip()
        wp_app_pwd = settings.get("wp_app_password", "").strip()

        if not (wp_url and wp_user and wp_app_pwd):
            return {
                "success": False,
                "platform": "wordpress",
                "message": "워드프레스 연동 정보(사이트 URL, 사용자명, 앱 비밀번호)가 설정되지 않았습니다. 설정 탭에서 입력해주세요."
            }

        endpoint = f"{wp_url}/wp-json/wp/v2/posts"
        auth_str = f"{wp_user}:{wp_app_pwd}"
        auth_header = f"Basic {base64.b64encode(auth_str.encode()).decode()}"

        payload = {
            "title": title,
            "content": content_html,
            "status": status  # "publish" or "draft"
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": auth_header,
                    "User-Agent": "AutoAffiliateStudio/1.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return {
                    "success": True,
                    "platform": "wordpress",
                    "post_id": data.get("id"),
                    "link": data.get("link"),
                    "status": data.get("status"),
                    "message": f"워드프레스에 성공적으로 등록되었습니다! (상태: {status})"
                }
        except Exception as e:
            return {
                "success": False,
                "platform": "wordpress",
                "message": f"워드프레스 발행 실패: {str(e)}"
            }

    def publish_to_tistory(self, title: str, content_html: str) -> dict:
        """티스토리 Open API 포스팅"""
        settings = get_settings()
        access_token = settings.get("tistory_access_token", "").strip()
        blog_name = settings.get("tistory_blog_name", "").strip()

        if not (access_token and blog_name):
            return {
                "success": False,
                "platform": "tistory",
                "message": "티스토리 연동 정보(Access Token, Blog Name)가 설정되지 않았습니다."
            }

        url = "https://www.tistory.com/apis/post/write"
        params = {
            "access_token": access_token,
            "output": "json",
            "blogName": blog_name,
            "title": title,
            "content": content_html,
            "visibility": "0"  # 0: 비공개, 3: 공개
        }
        data = urllib.parse.urlencode(params).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                return {
                    "success": True,
                    "platform": "tistory",
                    "url": res_data.get("tistory", {}).get("url"),
                    "message": "티스토리에 성공적으로 등록되었습니다."
                }
        except Exception as e:
            return {
                "success": False,
                "platform": "tistory",
                "message": f"티스토리 등록 실패: {str(e)}"
            }

    def export_naver_format(self, title: str, markdown_content: str) -> dict:
        """네이버 블로그용 스마트 서식 텍스트 변환 (원클릭 복사 최적화)"""
        # 마크다운을 네이버 에디터 친화적인 줄바꿈 및 강조 텍스트로 가공
        lines = markdown_content.split('\n')
        formatted_lines = []
        for line in lines:
            if line.startswith('## '):
                formatted_lines.append(f"\n[ {line.replace('## ', '').strip()} ]\n")
            elif line.startswith('### '):
                formatted_lines.append(f"\n▶ {line.replace('### ', '').strip()}\n")
            elif line.startswith('> '):
                formatted_lines.append(f"💡 {line.replace('> ', '').strip()}")
            elif line.startswith('- '):
                formatted_lines.append(f"• {line.replace('- ', '').strip()}")
            else:
                formatted_lines.append(line)

        naver_body = "\n".join(formatted_lines)
        return {
            "title": title,
            "body": naver_body,
            "tips": "네이버 블로그 스마트에디터에 그대로 붙여넣으면 소제목과 문단 구분이 최적화됩니다."
        }

    def export_threads_package(self, threads_data: dict) -> list:
        """쓰레드 5개 연속 포스팅 패키지 생성"""
        items = threads_data.get("thread_items", [])
        return [{
            "step": i + 1,
            "text": item,
            "char_count": len(item),
            "tips": "첫 댓글이나 프로필 링크를 반드시 안내하세요" if i == len(items)-1 else "공감형 훅 유지"
        } for i, item in enumerate(items)]
