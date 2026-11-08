import json
from core.llm_client import LLMClient

class AnalystAgent:
    """
    [직원 1: 시장/상품 분석관 '민수']
    - 역할: 쇼핑 링크 및 벤치마킹 블로그 포스팅을 심층 분석
    - 산출물: 타겟 페르소나, 핵심 소구점(USP), 결핍(Pain Point), 후킹 공식, 전략 브리핑
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.name = "민수 (시장/상품 분석관)"
        self.role = "Market & Benchmark Analyst"

    def analyze(self, product_info: dict, benchmark_text: str) -> str:
        system_prompt = f"""당신은 탑티어 제휴 마케팅 팀의 수석 '시장/상품 분석관 {self.name}'입니다.
당신의 역할은 사용자가 제공한 쇼핑몰 상품 정보와 '잘 나가는 상위 노출 벤치마크 블로그' 글을 정밀 분석하여,
동료 카피라이터가 최고의 전환율(CVR)을 내는 글을 쓸 수 있도록 '전략 브리핑 보고서'를 작성하는 것입니다.

[분석 지침]
1. 상품의 표면적 기능뿐만 아니라 실사용자가 진짜 가려워하는 핵심 결핍(Pain Point)을 찾아내세요.
2. 벤치마킹 글에서 '사람들이 왜 이 글을 끝까지 읽었는지' 후킹 요소와 스토리 흐름을 해체하세요.
3. 뻔한 광고성 찬양을 배제하고, 독자가 신뢰할 수밖에 없는 소구 전략을 제시하세요.
4. 카피라이터에게 전할 필수 지침(단점 언급 필수, 말투 방향 등)을 명문화하세요."""

        user_prompt = f"""[분석 대상 상품 정보]
- 상품명: {product_info.get('title', '미지정')}
- 판매처: {product_info.get('platform', '온라인 쇼핑몰')}
- 쇼핑 링크: {product_info.get('url', '')}
- 부가 정보/설명: {product_info.get('raw_text', '') or '기본 사양 참고'}
- 추출된 특징: {', '.join(product_info.get('extracted_features', []))}

[참고 벤치마크 (잘 나가는 상위 노출 글)]
{benchmark_text if benchmark_text else "별도 벤치마크 없음 (자체 바이럴 공식 적용)"}

위 정보를 바탕으로 전문적인 '상품 & 벤치마크 심층 분석 리포트'를 작성해주세요."""

        return self.llm.generate_chat(system_prompt, user_prompt, temperature=0.6)
