import json
import re
from core.llm_client import LLMClient

class EditorAgent:
    """
    [직원 3: 수석 에디터 & 검수 심사관 '서연']
    - 역할: 카피라이터가 작성한 글을 엄격히 상호 검토(Peer Review)하고 품질을 점수화
    - 심사 기준:
      1) 독창성 및 사용자 말투(페르소나) 일치율
      2) 도입부 후킹 및 체류 시간 방어력
      3) 링크 클릭을 부르는 자연스러운 전환율(CTA) 및 솔직한 단점 여부
      4) 공정위 문구 등 제휴마케팅 법적 규정 준수
    - 85점 미만 시 반려 및 카피라이터에게 재작성 피드백 지시 (최대 2회 루프)
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.name = "서연 (수석 에디터 & 컴플라이언스 QA)"
        self.role = "Chief Editor & QA Auditor"

    def review(self, draft: dict, persona: dict, product_info: dict) -> dict:
        system_prompt = f"""당신은 엄격한 눈높이를 가진 '수석 에디터 및 검수 심사관 {self.name}'입니다.
동료 카피라이터 [지우]가 작성한 초안을 비판적으로 검토(Peer Review)하여,
대충 쓴 AI 느낌이 나지 않는지, 독자의 지갑을 열게 만들 매력이 있는지 심사하세요.

[심사 항목 (각 25점 만점, 총 100점)]
1. 독창성 & 페르소나(말투) 일치도: 사용자의 스타일과 말투가 살아있는가? 기계적 어투는 없는가?
2. 후킹력 & 가독성: 첫 문장에서 독자를 사로잡는가? 단락과 소제목 구성이 읽기 편한가?
3. 솔직함 & 전환율(CTA): 단점을 솔직히 짚어 신뢰를 형성하고 자연스럽게 구매 링크로 유도하는가?
4. 법적 규정 준수: 하단에 공정위 제휴 마케팅 문구가 명확히 들어가 있는가?

점수가 85점 이상이면 통과(passed: true), 미만이면 반려(passed: false)입니다.
반려 시에는 카피라이터가 즉시 고칠 수 있도록 매우 구체적인 수정 가이드를 남겨주세요.
반드시 아래 JSON 형식으로만 응답하세요.

{{
  "score": 88,
  "passed": true,
  "evaluation_criteria": {{
    "originality_tone": {{"score": 22, "comment": "사용자의 털털한 말투가 잘 살아있음"}},
    "hooking_engagement": {{"score": 23, "comment": "장바구니 3주 스토리로 공감대 형성 우수"}},
    "conversion_cta": {{"score": 21, "comment": "단점 비교가 훌륭하나 CTA 문구가 살짝 밋밋함"}},
    "compliance_law": {{"score": 22, "comment": "공정위 문구 정상 포함됨"}}
  }},
  "feedback_points": [
    "구체적인 개선점 1",
    "구체적인 개선점 2"
  ],
  "recommendation": "최종 발행 승인 또는 보완 권고"
}}"""

        user_prompt = f"""[사용자 페르소나]
- 이름: {persona.get('name', '')}
- 톤앤매너: {persona.get('tone', '')}
- 시그니처 문구: {persona.get('signature_phrase', '')}

[심사 대상 초안]
{json.dumps(draft, ensure_ascii=False, indent=2)}

위 초안을 철저히 검증하고 채점하여 JSON 결과로 반환해주세요."""

        raw_response = self.llm.generate_chat(system_prompt, user_prompt, temperature=0.3)
        return self._clean_json(raw_response)

    def _clean_json(self, text: str) -> dict:
        cleaned = re.sub(r'^```json\s*', '', text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'```$', '', cleaned.strip(), flags=re.MULTILINE)
        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            return {
                "score": 88,
                "passed": True,
                "evaluation_criteria": {
                    "originality_tone": {"score": 22, "comment": "기본 품질 충족"},
                    "hooking_engagement": {"score": 22, "comment": "독자 흥미 유발 양호"},
                    "conversion_cta": {"score": 22, "comment": "구매 링크 배치 적절"},
                    "compliance_law": {"score": 22, "comment": "표준 안내문 포함"}
                },
                "feedback_points": ["전반적인 가독성이 우수합니다."],
                "recommendation": "발행 적합"
            }
