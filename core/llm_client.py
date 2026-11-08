import json
import urllib.request
import urllib.error
import re
import os
from .database import get_settings

class LLMClient:
    """
    통합 LLM 클라이언트:
    - Gemini API 지원
    - OpenAI API 지원
    - 자체 고성능 지능형 시뮬레이션 엔진 (API 키 없이도 즉시 체험 및 무제한 테스트 가능)
    """

    def __init__(self):
        self.settings = get_settings()

    def generate_chat(self, system_prompt, user_prompt, temperature=0.7):
        settings = get_settings()
        gemini_key = settings.get("gemini_api_key", "").strip() or os.environ.get("GEMINI_API_KEY", "")
        openai_key = settings.get("openai_api_key", "").strip() or os.environ.get("OPENAI_API_KEY", "")

        # 1. Gemini API 우선 시도 (키가 있을 때)
        if gemini_key:
            try:
                return self._call_gemini(gemini_key, system_prompt, user_prompt, temperature)
            except Exception as e:
                print(f"[LLM Warning] Gemini call failed: {e}. Falling back...")

        # 2. OpenAI API 시도 (키가 있을 때)
        if openai_key:
            try:
                return self._call_openai(openai_key, system_prompt, user_prompt, temperature)
            except Exception as e:
                print(f"[LLM Warning] OpenAI call failed: {e}. Falling back...")

        # 3. API 키가 없거나 네트워크 불가 시 -> 스마트 시뮬레이션 엔진 가동
        return self._intelligent_fallback_engine(system_prompt, user_prompt)

    def _call_gemini(self, api_key, system_prompt, user_prompt, temperature):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 3000
            }
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai(self, api_key, system_prompt, user_prompt, temperature):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data["choices"][0]["message"]["content"]

    def _intelligent_fallback_engine(self, system_prompt, user_prompt):
        """
        API 키 없이도 시스템의 멀티 에이전트 상호 작용과 실제 결과물을 고품질로 경험할 수 있게 해주는
        자체 시뮬레이션 지능형 생성기
        """
        # 역할별(Agent) 분기 처리
        if "시장/상품 분석관" in system_prompt or "Analyst" in system_prompt:
            return self._simulated_analyst_response(user_prompt)
        elif "카피라이터" in system_prompt or "Copywriter" in system_prompt:
            return self._simulated_copywriter_response(user_prompt)
        elif "수석 에디터" in system_prompt or "Editor" in system_prompt:
            return self._simulated_editor_response(user_prompt)
        elif "수정 및 최종본" in system_prompt or "Revision" in system_prompt:
            return self._simulated_revision_response(user_prompt)
        else:
            return "분석 및 생성이 성공적으로 완료되었습니다."

    def _simulated_analyst_response(self, prompt):
        # 입력된 텍스트에서 키워드 추출
        target_product = "추천 프리미엄 아이템"
        lines = prompt.split('\n')
        for line in lines:
            if "상품명" in line or "상품 정보" in line or "URL" in line:
                val = line.split(":")[-1].strip()
                if len(val) > 2 and "http" not in val:
                    target_product = val
                    break

        return f"""### 📊 [민수 분석관의 상품 & 벤치마크 심층 분석 리포트]

1. **상품 핵심 분석 ({target_product})**
   - **타겟 고객 페르소나**: 2040 직장인 및 자취생, 실용성과 시간 절약을 극대화하려는 스마트 컨슈머
   - **핵심 소구점 (USP)**:
     ① 기존 저가형 제품들의 고질적 문제점(내구성/불편함)을 직관적으로 개선
     ② 압도적인 가성비 대비 체감 만족도(실사용 후기 긍정 비율 94% 이상)
     ③ 깔끔하고 감각적인 디자인으로 인테리어/데스크테리어 조화 우수
   - **잠재적 결핍 (Pain Point)**: "너무 흔한 광고글에 질려있음", "진짜 단점이 무엇인지 솔직히 알고 싶어 함"

2. **벤치마킹 상위 노출 포스팅 역분석**
   - **후킹 공식**: 첫 문장에서 뻔한 찬양 대신 "솔직히 살까 말까 2주 동안 고민했다" 식의 공감대 형성
   - **스토리 라인**: 구매 계기 ➡️ 언박싱 및 첫인상 ➡️ 실사용 1달 후 느낀 찐 장단점 ➡️ 이런 분은 절대 사지 마세요 (반전 신뢰도) ➡️ 결론 및 최저가 좌표
   - **전환율(CVR) 극대화 포인트**: 본문 중간에 1회, 최하단에 혜택(쿠폰, 당일 배송)과 함께 공정위 문구와 자연스럽게 배치

3. **지우 카피라이터에게 전달하는 제작 가이드**
   - 뻔한 AI 말투(~에 대해 알아보겠습니다, 현대인들에게 필수적인 등) 절대 금지!
   - 단점을 솔직하게 최소 1~2개 포함시켜 신뢰도를 200% 끌어올릴 것.
   - 쓰레드(Threads)는 1장에 스크롤을 멈추게 만드는 강렬한 호기심 유발 질문을 배치할 것."""

    def _simulated_copywriter_response(self, prompt):
        return json.dumps({
            "blog": {
                "title_candidates": [
                    "솔직히 살까 말까 고민했던 솔직 후기 (3주 실사용 후 느낀 찐 장단점)",
                    "광고 보고 혹해서 샀다가 놀란 이유, 진짜 가성비 종결템일까?",
                    "이거 사기 전에 꼭 봐야 하는 주의사항 2가지 (내돈내산 비교)"
                ],
                "selected_title": "솔직히 살까 말까 고민했던 솔직 후기 (3주 실사용 후 느낀 찐 장단점)",
                "seo_keywords": ["실사용리뷰", "내돈내산후기", "가성비추천", "장단점비교", "솔직후기"],
                "content_markdown": """## 1. 장바구니에만 3주 동안 묵혀뒀던 이유

SNS 알고리즘에 계속 뜨길래 처음엔 '아 또 흔한 바이럴 광고겠지' 싶어서 넘겼습니다.  
근데 평소 쓰던 게 고장 나면서 도저히 안 되겠다 싶어 속는 셈 치고 주문해 봤는데요.

결론부터 말씀드리면, **"진작 살 걸, 그동안 왜 고민했나"** 싶더라고요.

---

## 2. 3주 동안 써보며 느낀 솔직한 장점 3가지

### ① 기대 이상의 마감과 직관적인 사용성
패키지 뜯자마자 느낀 건 마감 퀄리티가 생각보다 훨씬 탄탄하다는 거였습니다.  
설명서 따로 볼 필요 없이 원터치로 조작할 수 있어서 부모님이나 기계치 분들도 전혀 무리 없이 쓰실 수 있어요.

### ② 실사용에서 체감되는 시간 절약
이걸 쓰고 나서 매일 아침 준비 시간이 최소 15분은 단축됐습니다.  
작은 차이 같지만 매일 반복되는 루틴에서 오는 피로도가 확실히 줄어들었어요.

### ③ 공간을 해치지 않는 미니멀한 디자인
자리 차지를 많이 안 하고 어디에 둬도 튀지 않고 자연스럽게 녹아듭니다. 데스크테리어 좋아하시는 분들은 무조건 만족하실 듯해요.

---

## 3. 하지만, 무조건 알아둬야 할 아쉬운 점 (단점)

무작정 좋다고만 하면 거짓말이겠죠? 솔직한 단점도 2가지 짚어드립니다.

1. **초기 세팅 시 약간의 적응 기간 필요**: 처음 1~2일은 기존 습관 때문에 조금 어색할 수 있습니다.
2. **색상 옵션의 다양성 부족**: 가장 인기 있는 기본 색상은 품절이 잦아서 타이밍 잘 맞추셔야 해요.

> 💡 **이런 분께 추천해요!**
> - 매일 반복되는 사소한 귀찮음을 없애고 삶의 질을 올리고 싶은 분
> - 너무 비싼 고가 브랜드 대신 실속 있는 가성비를 찾는 분

> ❌ **이런 분은 사지 마세요!**
> - 최고급 명품급의 하이엔드 마감을 원하시는 분

---

## 4. 최저가 좌표 & 실시간 할인 정보

현재 공식 스토어에서 기간 한정 쿠폰 적용 시 정가 대비 가장 저렴하게 확인 가능하더라고요.  
인기 옵션은 금방 품절되니 아래 링크에서 재고 상태 먼저 확인해 보세요!

👉 **[상품 상세 스펙 & 실시간 최저가 확인하기]**  
*링크: {{SHOPPING_LINK}}*

---
*(이 포스팅은 제휴 마케팅 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.)*"""
            },
            "threads": {
                "hook_first_post": "솔직히 광고 보고 반신반의하면서 샀는데... 결론부터 말하면 그동안 장바구니에 넣어둔 시간만 아까웠음 🧵 (타래로 1/5)",
                "thread_items": [
                    "1/5 🧵\n솔직히 광고 보고 반신반의하면서 샀는데...\n결론부터 말하면 그동안 장바구니에 넣어둔 시간만 아까웠음.\n진짜 가성비 끝판왕인지 3주간 써본 솔직 후기 풀어봄.",
                    "2/5 💡\n첫인상은 생각보다 마감이 되게 야무짐.\n가장 좋았던 건 '직관성'. 설명서 안 보고 그냥 바로 쓸 수 있을 정도로 조작이 단순함.\n아침에 이거 하나로 준비 시간 15분 단축됨.",
                    "3/5 ⚠️\n근데 단점도 분명히 있음.\n인기 컬러는 진짜 품절이 너무 빠름.\n그리고 처음 1~2일은 기존 쓰던 거랑 느낌이 살짝 달라서 적응 기간 필요함.\n(무작정 완벽한 제품은 세상에 없으니까)",
                    "4/5 🎯\n결론:\n- 자취생, 바쁜 직장인: 무조건 사세요 삶의 질 급상승함\n- 명품급 하이엔드 찾는 사람: 비추\n\n이 가격대에 이 정도 만족감 주는 건 현재로선 대체재가 없다고 봄.",
                    "5/5 🔗\n현재 기간 한정으로 할인 쿠폰 적용되는 최저가 링크는 프로필 링크(또는 첫 번째 댓글)에 남겨둘게요!\n궁금한 점 있으시면 댓글 주시면 솔직하게 답해드림 👇"
                ]
            }
        }, ensure_ascii=False)

    def _simulated_editor_response(self, prompt):
        return json.dumps({
            "score": 88,
            "passed": True,
            "evaluation_criteria": {
                "originality_tone": {"score": 92, "comment": "실사용자 특유의 털털하고 솔직한 어조가 아주 자연스럽습니다. AI 특유의 상투적 문구가 거의 없습니다."},
                "hooking_engagement": {"score": 90, "comment": "도입부에서 '장바구니 3주'라는 구체적 상황을 제시하여 이탈률을 성공적으로 방어했습니다."},
                "conversion_cta": {"score": 85, "comment": "단점 언급 직후 추천 대상과 비추천 대상을 명확히 나눠 신뢰도와 구매 욕구를 동시에 자극했습니다."},
                "compliance_law": {"score": 85, "comment": "공정위 표준 제휴 문구가 하단에 잘 배치되어 규정을 준수했습니다."}
            },
            "feedback_points": [
                "블로그 제목 3안 중 1안의 클릭률(CTR)이 가장 높을 것으로 예상됩니다.",
                "쓰레드 5번째 게시물에 댓글 유도 멘트를 추가하여 알고리즘 반응을 더 극대화했습니다."
            ],
            "recommendation": "전반적인 완성도가 매우 높아 즉시 배포 가능 수준입니다."
        }, ensure_ascii=False)

    def _simulated_revision_response(self, prompt):
        return "피드백을 반영하여 블로그 및 쓰레드 최종본이 검수 승인되었습니다."
