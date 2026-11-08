import json
import re
from core.llm_client import LLMClient

class CopywriterAgent:
    """
    [직원 2: 맞춤형 카피라이터 '지우']
    - 역할: 분석관의 브리핑 보고서와 사용자의 고유 페르소나/말투를 반영하여 블로그 & 쓰레드 초안 작성
    - 산출물: JSON 포맷 (블로그 제목 후보, 블로그 본문 Markdown, 쓰레드 5개 연속 포스트)
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.name = "지우 (스타일 맞춤 카피라이터)"
        self.role = "Persona Copywriter"

    def write_initial_draft(self, product_info: dict, analyst_brief: str, persona: dict) -> dict:
        system_prompt = f"""당신은 사용자 맞춤형 '페르소나 카피라이터 {self.name}'입니다.
당신의 임무는 [민수 분석관]의 브리핑과 [사용자의 고유 스타일/말투]를 100% 흡수하여,
1) 긴 호흡의 바이럴 블로그 포스팅
2) 반응 폭발형 쓰레드(Threads) 연속 게시물(5개 타래)
을 동시에 작성하는 것입니다.

[지켜야 할 핵심 원칙]
1. 말투 복제: 사용자가 정의한 톤앤매너와 시그니처 말투를 본문 전반에 자연스럽게 녹여내세요.
2. AI 냄새 완전 제거: "~에 대해 알아보겠습니다", "현대인들에게 필수템", "다양한 매력을 지닌" 같은 뻔한 문장 절대 금지!
3. 신뢰의 핵심은 솔직한 '단점'입니다. 장점만 나열하지 말고 실사용자 입장에서 아쉬웠던 점을 반드시 디테일하게 서술하세요.
4. 블로그 포스팅 하단에는 제공된 쇼핑 링크({{SHOPPING_LINK}})와 공정위 제휴 문구를 자연스럽게 넣으세요.
5. 출력은 반드시 유효한 JSON 형식이어야 합니다.

[JSON 출력 포맷 예시]
{{
  "blog": {{
    "title_candidates": ["제목1", "제목2", "제목3"],
    "selected_title": "가장 후킹력 좋은 대표 제목",
    "seo_keywords": ["키워드1", "키워드2", "키워드3"],
    "content_markdown": "블로그 마크다운 본문..."
  }},
  "threads": {{
    "hook_first_post": "첫 번째 스레드 훅...",
    "thread_items": [
      "1/5 🧵 본문...",
      "2/5 💡 본문...",
      "3/5 ⚠️ 본문...",
      "4/5 🎯 본문...",
      "5/5 🔗 링크 및 댓글 유도..."
    ]
  }}
}}"""

        user_prompt = f"""[사용자의 스타일 페르소나 설정]
- 페르소나 이름: {persona.get('name', '솔직 리뷰어')}
- 지향 톤앤매너: {persona.get('tone', '솔직하고 털털한 어조')}
- 상세 설명: {persona.get('description', '')}
- 시그니처 문구: {persona.get('signature_phrase', '')}
- 말투 예시 샘플:
{persona.get('sample_text', '')}

[상품 기본 정보]
- 상품명: {product_info.get('title', '상품')}
- 링크: {product_info.get('url', '{{SHOPPING_LINK}}')}

[민수 분석관의 브리핑 리포트]
{analyst_brief}

위 가이드에 맞춰 사용자 스타일이 살아 숨 쉬는 블로그 및 쓰레드 글을 작성하여 JSON으로 출력해주세요."""

        raw_response = self.llm.generate_chat(system_prompt, user_prompt, temperature=0.7)
        return self._clean_json(raw_response)

    def revise_draft(self, original_draft: dict, editor_feedback: dict, persona: dict) -> dict:
        """에디터 서연의 검수 피드백을 반영하여 수정본 작성"""
        system_prompt = f"""당신은 카피라이터 {self.name}입니다.
[서연 수석 에디터]가 지적한 감점 요인과 수정 피드백을 면밀히 분석하여,
사용자의 스타일을 유지하면서도 완성도를 100점 수준으로 끌어올린 수정본을 작성해야 합니다.
반드시 이전과 동일한 JSON 규격으로 출력하세요."""

        user_prompt = f"""[이전 초안]
{json.dumps(original_draft, ensure_ascii=False, indent=2)}

[서연 에디터의 검수 및 수정 지시사항]
- 종합 점수: {editor_feedback.get('score', 0)}점
- 평가 의견: {json.dumps(editor_feedback.get('evaluation_criteria', {}), ensure_ascii=False)}
- 구체적 개선 요구사항: {json.dumps(editor_feedback.get('feedback_points', []), ensure_ascii=False)}

위 피드백을 반영하여 완벽하게 수정한 JSON 결과를 출력해주세요."""

        raw_response = self.llm.generate_chat(system_prompt, user_prompt, temperature=0.5)
        return self._clean_json(raw_response)

    def _clean_json(self, text: str) -> dict:
        """JSON 마크다운 코드블록 제거 및 파싱"""
        cleaned = re.sub(r'^```json\s*', '', text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'```$', '', cleaned.strip(), flags=re.MULTILINE)
        try:
            return json.loads(cleaned)
        except Exception:
            # 매칭 시도
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            # 실패 시 기본 구조체 반환
            return {
                "blog": {
                    "title_candidates": ["솔직한 실사용 리뷰"],
                    "selected_title": "솔직한 실사용 리뷰 및 장단점 분석",
                    "seo_keywords": ["내돈내산", "솔직리뷰"],
                    "content_markdown": text
                },
                "threads": {
                    "hook_first_post": "솔직하게 써보고 남기는 찐 후기 타래 🧵",
                    "thread_items": [text[:200], text[200:400], text[400:600]]
                }
            }
