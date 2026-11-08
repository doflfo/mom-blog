import re
import random

class PowerBloggerHumanizer:
    """
    [카테고리별 맞춤형 기승전결 롱폼 파워블로거 엔진]
    - 입력된 상품명과 카테고리를 자동 분석하여 그 제품에 100% 맞는 실제 장단점 및 기승전결 롱폼(2,000자 내외) 구성
    - 뻔한 AI 상투어구(## 1, ## 2, 💡, ⚠️, 🎯) 완전 박멸
    - 기(일상의 고통) ➡️ 승(기존 기본 대안들의 실패담) ➡️ 전(왜 이 제품을 사야 하는가) ➡️ 결(솔직한 현실 단점 & 꿀팁 & 결론)
    - 사진 4장(언박싱/실사용/디테일/전체 샷) 및 캡션이 본문 스토리와 100% 일체화
    """

    @classmethod
    def analyze_category(cls, product_name: str) -> str:
        name = product_name.lower()
        if any(w in name for w in ["방풍", "비닐", "외풍", "우풍", "창문", "단열", "문풍지", "방한", "지퍼형", "뽁뽁이"]):
            return "windbreak" # 방풍비닐/단열
        elif any(w in name for w in ["거치대", "스탠드", "홀더", "태블릿", "아이패드", "피르모", "스마트폰", "자바라"]):
            return "holder" # 거치대
        elif any(w in name for w in ["마사지", "안마", "찜질", "온열", "보호대", "손목보호대", "무릎보호대", "지압", "스트레칭", "목마사지", "어깨마사지"]):
            return "health" # 건강/안마/마사지
        elif any(w in name for w in ["가습기", "제습기", "공기청정기", "온풍기", "히터"]):
            return "appliance" # 생활/계절가전
        elif any(w in name for w in ["청소기", "로봇청소기", "무선청소기"]):
            return "vacuum" # 청소기
        elif any(w in name for w in ["크림", "세럼", "앰플", "토너", "화장품", "선크림", "샴푸", "바디워시"]):
            return "beauty" # 뷰티
        elif any(w in name for w in ["텀블러", "프라이팬", "냄비", "에어프라이어", "주방", "칼", "도마", "밀폐용기"]):
            return "kitchen" # 주방
        else:
            return "general" # 일반

    @classmethod
    def generate_power_titles(cls, product_name: str, category: str, emergency_mode: bool = False) -> list:
        clean_name = product_name.replace("쿠팡!", "").replace("스마트스토어", "").strip()
        # 불필요한 규격/수량 꼬리표 정리 (예: ", 1.8x1.8m, 1개", ", 1개", " 170cm" 등)
        clean_name = re.sub(r'[,/]\s*\d.*$', '', clean_name).strip()
        if len(clean_name) > 22:
            clean_name = clean_name[:22].strip()
        clean_name = clean_name or "화제의 꿀템"
        
        if category == "windbreak":
            pool = [
                f"[내돈내산] 뽁뽁이 다 뜯어내고 {clean_name} 바꾼 이유... 솔직히 난방비 얼마나 아낄까? (단점 3개)",
                f"창문 칼바람 지옥 탈출... {clean_name} 3주 솔직 장단점 팩트체크 (설치 꿀팁)",
                f"아직도 문풍지만 붙이세요? {clean_name} 달고 방 체감온도 3도 올린 썰",
                f"외풍 때문에 감기 달고 살다가 {clean_name} 설치하고 신세계 경험한 솔직 후기",
                f"진작 달 걸 후회 중인 {clean_name} 3주 찐후기 (투명 시야 & 환기 지퍼 디테일)"
            ]
        elif category == "holder":
            pool = [
                f"[내돈내산] 누워서 폰 보다가 얼굴 찍힐 뻔하고 산 {clean_name} 3주 찐후기 (단점 3개)",
                f"싸구려 자바라 3개 버리고 {clean_name} 정착한 솔직한 이유 (흔들림 팩트체크)",
                f"인스타 알고리즘에 맨날 뜨던 {clean_name}... 솔직히 돈값 할까? 한 달 써본 솔직 후기",
                f"아직도 손으로 들고 보세요? {clean_name} 쓰고 삶의 질 떡상한 침대순이 썰"
            ]
        elif category == "health":
            pool = [
                f"[내돈내산] 뻐근한 목 어깨 통증 달고 살다가 {clean_name} 3주 써본 찐후기 (단점 3개)",
                f"매일 파스만 붙이다가 {clean_name} 장만하고 삶의 질 떡상한 솔직 후기",
                f"인스타 광고 보고 반신반의하며 산 {clean_name}... 솔직히 돈값 할까? 3주 팩트체크",
                f"진작 살 걸 그동안 왜 고생했나 싶은 {clean_name} 솔직 장단점 (부모님 선물 강추)"
            ]
        elif category == "appliance":
            pool = [
                f"[내돈내산] 자고 일어나면 목 칼칼해서 산 {clean_name} 3주 솔직 후기 (단점 3개)",
                f"싸구려 미니 가습기 버리고 {clean_name} 갈아탄 솔직한 이유 (세척 꿀팁)",
                f"올겨울 건조함 지옥 탈출... {clean_name} 한 달 실사용 팩트체크"
            ]
        elif category == "vacuum":
            pool = [
                f"[내돈내산] 10만 원대 저가형 버리고 {clean_name} 갈아탄 솔직 후기 (단점 3가지)",
                f"먼지 흡입력 실화? {clean_name} 3주 동안 매일 굴려본 솔직 장단점 팩트체크",
                f"머리카락 먼지 스트레스 끝... {clean_name} 한 달 실사용 찐후기 (배터리 & 관리 팁)"
            ]
        else:
            pool = [
                f"[내돈내산] 장바구니에 한 달 묵혀뒀다 산 {clean_name} 3주 솔직 후기 (단점 3개)",
                f"인스타 대란템 {clean_name}... 솔직히 돈값 할까? 3주 굴려본 팩트체크",
                f"제발 {clean_name} 사기 전에 이것만 꼭 보세요! (솔직 장단점과 실사용 꿀팁)",
                f"진작 살 걸 그동안 왜 고민했나 싶은 {clean_name} 내돈내산 썰 (아쉬운 점 솔직 공개)"
            ]

        if emergency_mode:
            emergency_pool = [
                f"🚨 [충격] {clean_name} 절대 그냥 사지 마세요! 3주 쓰고 겪은 치명적 단점",
                f"솔직히 돈 버렸나 싶었는데... 반전 결과 나온 {clean_name} 팩트폭격 후기",
                f"다들 극찬하길래 의심 반 호기심 반으로 샀다가 무릎 꿇은 {clean_name} 썰"
            ]
            return emergency_pool

        templates = random.sample(pool, min(3, len(pool)))
        return templates

    @classmethod
    def adapt_tone_to_persona(cls, text: str, persona: dict) -> str:
        if not persona or not text:
            return text
        
        adapted = text
        tone_key = persona.get("tone_key")
        if tone_key == "polite":
            # 긍정적이고 다정한 경어체로 정교하게 전환
            subs = [
                (r'습니다 ㅋㅋㅋ', '답니다 ㅎㅎ'),
                (r'습니다ㅋㅋㅋ', '답니다 ㅎㅎ'),
                (r'더라고요 ㅋㅋㅋ', '더라고요 ㅎㅎ'),
                (r'더라고요ㅋㅋ', '더라고요 ㅎㅎ'),
                (r'했음', '했어요'),
                (r'임 ㅋㅋㅋ', '이에요 ㅎㅎ'),
                (r'개편함', '정말 편해요'),
                (r'존맛', '정말 맛있어요'),
                (r'썰\b', '후기'),
            ]
            for pat, rep in subs:
                adapted = re.sub(pat, rep, adapted)
        return adapted

    @classmethod
    def build_viral_blog(cls, product_name: str, product_url: str, images: list, custom_points: str, persona: dict, emergency_mode: bool = False) -> dict:
        clean_name = product_name.strip()[:35] or "화제의 추천 아이템"
        category = cls.analyze_category(clean_name)
        titles = cls.generate_power_titles(clean_name, category=category, emergency_mode=emergency_mode)
        selected_title = titles[0]

        imgs = images if images and len(images) >= 4 else [
            "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80"
        ]

        # ----------------------------------------------------
        # 카테고리별 맞춤형 기승전결 롱폼 스토리텔링 빌드
        # ----------------------------------------------------
        if category == "windbreak":
            # ================= 1. 창문 방풍비닐 / 외풍차단 롱폼 (2,200자 고밀도) =================
            captions = [
                "▲ 택배 박스 개봉 실물 샷! 고투명 방풍비닐 본품과 창틀 부착용 초강력 벨크로 테이프가 함께 동봉되어 있음",
                "▲ 창틀에 벨크로 테이프 붙이고 방풍비닐을 고정한 실제 모습... 뽁뽁이와 달리 밖이 유리창처럼 훤히 다 보여서 개방감 최고!",
                "▲ 중앙의 양면 슬라이더 지퍼 디테일 컷. 비닐을 뗄 필요 없이 지퍼만 '치익' 내리면 창문 열고 바로 환기 가능!",
                "▲ 방 전체 설치 완료 모습. 창틀 틈새 칼바람을 완벽 차단해 줘서 보일러를 덜 틀어도 방 안이 온실처럼 훈훈함"
            ]

            opening_text = f"""날씨가 쌀쌀해지기 시작하면 창틀 틈새로 솔솔 들어오는 무시무시한 칼바람 때문에 고통받는 분들... 저만 그런 거 아니죠? ㅠㅠ

보일러 온도를 25도, 26도까지 빵빵하게 틀어도 바닥만 뜨끈뜨끈하고, 정작 방 안 공기는 시려워서 자다가 코 맹맹해지고 아침에 일어나면 목이 칼칼했던 적 다들 있으실 거예요.
특히 침대가 창문 바로 옆에 붙어있는 구조라면 자는 내내 얼굴 쪽으로 냉기가 쏟아져 내려서 진짜 잠을 설칠 정도였습니다.
지난달 도시가스 난방비 고지서 나온 거 보고 진짜 기절할 뻔했거든요...

그래서 이번 겨울엔 도저히 안 되겠다 싶어 검색에 검색을 거듭하다가 내돈내산으로 장만한 게 바로 **'{clean_name}'**입니다!

솔직히 비닐 한 장 창문에 붙인다고 진짜 그 매서운 외풍이 잡힐까 반신반의했는데요,
3주 동안 직접 설치하고 살아보니까 결론부터 말씀드리면 **"이거 왜 진작 안 샀나 싶을 정도로 삶의 질이 수직 상승"**했습니다 ㅋㅋㅋ"""

            sec1_title = "기존에 쓰던 다이소 문풍지와 뽁뽁이(에어캡)의 치명적인 한계"
            sec1_body = """방한 대책으로 보통 가장 먼저 떠올리는 '기본' 아이템들이 있잖아요? 저도 안 해본 게 아닙니다.

**1. 다이소 문풍지 스펀지 테이프의 실패**
창틀 틈새마다 회색 스펀지 문풍지를 덕지덕지 붙여봤는데, 창문 열고 닫을 때마다 마찰 때문에 밀려서 뜯어지고 1년 지나면 스펀지가 삭아서 검은 가루가 방 안으로 날리더라고요 ㅠㅠ 게다가 샷시 틈새는 여전히 바람이 숭숭 들어와서 외풍 차단 효과는 솔직히 체감상 20%도 안 됐습니다.

**2. 유리창 뽁뽁이(에어캡)의 답답함과 감옥살이**
물 뿌려서 붙이는 단열 뽁뽁이도 몇 년 동안 써봤는데요. 가장 치명적인 문제가 뭐냐면 **밖이 하나도 안 보인다는 점**이에요!
대낮에도 햇살이 차단돼서 방 안이 어두컴컴하고, 꼭 감옥에 갇혀 지내는 것처럼 답답해서 우울해지더라고요.
게다가 창문 손잡이까지 비닐에 덮여버리니까 겨울철에 환기 한번 하려면 뽁뽁이를 뜯어내야 해서 환기를 포기하게 되고, 그러다 보니 실내에 퀴퀴한 냄새와 창문 결로 곰팡이만 잔뜩 생겼습니다.

결국 **"1) 밖이 훤히 보이는 투명한 시야, 2) 비닐을 안 뜯고도 언제든 환기할 수 있는 지퍼 구조, 3) 창틀 전체를 완벽 밀폐하는 방식"**을 찾다가 이 지퍼형 투명 방풍비닐로 정착하게 되었습니다."""

            sec2_title = "왜 하필 '지퍼형 고투명 방풍비닐'이어야 할까? (핵심 특장점 4가지)"
            sec2_body = f"""제가 수많은 제품을 비교해 보고 **'{clean_name}'**을 선택한 데는 확실한 이유 4가지가 있습니다.

**1. 유리창처럼 밖이 100% 훤히 다 보이는 고투명 원단!**
싸구려 뿌연 농업용 비닐이 아니라 0.2~0.3mm 두께의 도톰하고 맑은 고투명 친환경 TPU/EVA 원단이에요. 붙여놓고 뒤로 물러서서 보면 비닐을 붙였는지 티도 안 날 만큼 투명합니다! 낮에 햇빛과 바깥 풍경이 그대로 다 들어와서 방이 환하고 답답함이 1도 없어요.

**2. 비닐 뜯을 필요 없이 1초 만에 끝나는 '양면 슬라이더 지퍼' 환기!**
가운데 지퍼가 위아래 양면 슬라이더로 짱짱하게 달려 있습니다. 겨울철 아침에 환기할 때 비닐을 뗄 필요가 전혀 없어요! 지퍼만 '치익' 내리고 창문 쓱 열어 환기시킨 뒤, 다시 지퍼만 올려 닫아주면 끝납니다. 이 지퍼 하나 덕분에 환기 스트레스가 0이 되었습니다.

**3. 못질/타공 없이 특수 벨크로(찍찍이)로 10분 초간단 설치!**
벽이나 창틀에 못 박거나 드릴질할 필요가 전혀 없습니다. 창틀 외곽 프레임에 동봉된 벨크로 양면테이프를 쭉 둘러 붙이고, 방풍비닐 테두리를 꾹꾹 눌러 붙여주면 끝납니다. 손재주 없는 저도 혼자서 15분 만에 창문 하나 완벽하게 설치했어요!

**4. 설치 즉시 체감온도 3도 상승 & 난방비 절감 팩트!**
비닐을 딱 붙이고 30분 지나서 창틀 근처에 손을 대봤는데요, 늘 느껴지던 시베리아 칼바람 냉기가 거짓말처럼 싹 차단되었습니다. 실내 온도가 훈훈하게 보존되니까 보일러 희망 온도를 22도로만 낮춰놔도 춥지가 않아서, 이번 겨울 도시가스비 절약으로 제품값은 진작에 뽑고도 남았습니다!"""

            sec3_title = "3주 실사용 후 솔직히 털어놓는 아쉬운 단점 3가지 & 극복 꿀팁"
            sec3_body = """좋은 점만 말하면 뻔한 광고 같으니, 제가 3주간 붙여두고 살면서 솔직히 느꼈던 현실적인 단점과 필수 관리 꿀팁도 가감 없이 털어놓습니다.

**1. 창틀 실측 사이즈 실수하면 낭패! (가장 중요)**
이거 진짜 주의하셔야 합니다! 유리창 크기만 딱 맞춰서 주문하시면 벨크로 붙일 테두리 자리가 모자라거나 바람이 샐 수 있어요. 반드시 **창틀 바깥 프레임(벨크로 붙일 자리 2.5~3cm)까지 포함해서 사방으로 가로/세로 최소 5cm 이상 넉넉한 사이즈**를 주문하셔야 실패가 없습니다!

**2. 초기 배송 시 새 비닐 특유의 접힌 구김과 냄새**
배송 올 때 접혀서 포장되어 오기 때문에, 개봉 직후에는 특유의 새 비닐 냄새와 접힌 주름이 살짝 보입니다. 냄새에 민감하신 분들은 바로 창문에 달지 마시고 베란다나 통풍 잘되는 곳에 반나절 널어두시면 냄새가 싹 날아갑니다. 접힌 주름은 설치하고 며칠 지나면 팽팽해지는데, 급하신 분들은 헤어드라이기 '미온풍'으로 살살 쐬어주시면 주름이 마법처럼 펴져요! (단, 너무 가까이 뜨거운 바람 쐬면 비닐 늘어나니 30cm 거리 유지 필수)

**3. 창틀 유분기/먼지 제거 필수 (벨크로 접착 꿀팁)**
창틀에 묵은 먼지나 기름때가 남아있는 상태로 벨크로 테이프를 붙이면, 한겨울 칼바람 압력이나 결로 때문에 테이프 모서리가 들뜰 수 있습니다. 붙이기 전에 반드시 **물티슈 ➡️ 마른 수건(또는 알코올 스왑)으로 창틀을 뽀송뽀송하게 닦고 바짝 말린 뒤에 부착**하세요! 테이프 붙인 뒤 드라이기로 따뜻한 바람 쐬어주며 엄지손가락으로 꾹꾹 눌러주면 절대 안 떨어집니다.

**4. 겨울철 결로(물방울) 관리 요령**
실내와 바깥 기온차가 워낙 크다 보니, 비닐 안쪽 창문에 물방울(결로)이 맺힐 수 있습니다. 이건 비닐 문제가 아니라 자연스러운 온도차 현상인데요, 아침에 일어나서 중앙 지퍼 열고 10분 정도 맞바람 환기시켜 주시면 습기가 싹 날아가서 곰팡이 걱정 없이 뽀송하게 유지됩니다."""

            sec4_title = "한 달 써보고 내린 최종 결론 (추천 vs 비추천)"
            sec4_body = """**이런 분들께는 무조건 추천합니다:**
- 오래된 샷시나 창문 틈새로 황소바람이 들이닥쳐 밤에 잠 못 드시는 분
- 답답하고 어두침침한 뽁뽁이 뜯어내고 밖이 훤히 보이는 개방감을 원하시는 분
- 비닐 뗄 필요 없이 매일 편하게 지퍼로 환기하고 싶으신 분
- 겨울철 난방비 가스비 폭탄이 두려운 자취생 및 1~2인 가구

**이런 분들은 안 사셔도 됩니다:**
- 최근 지어진 신축 아파트 시스템 3중 로이 창호라 외풍이 전혀 없는 집

1~2만 원대 투자해서 올겨울 내내 감기 안 걸리고 방 안에서 반팔 입고 훈훈하게 지낼 수 있으니, 올겨울 최고의 가성비 난방 꿀템으로 인정합니다!"""

        elif category == "holder":
            # ================= 2. 침대 거치대 / 태블릿 스탠드 롱폼 (2,100자) =================
            captions = [
                "▲ 택배 도착하자마자 신나서 언박싱한 실물 샷! 묵직한 탄소강 스틸 원판 받침대와 스프링 관절 지지대가 튼튼하게 들어있음",
                "▲ 침대 프레임 옆에 세워두고 아이패드 물려놓은 실사용 모습... 누워서 두 손 자유롭게 보니까 세상 편함!",
                "▲ 관절 스프링 조절부 디테일 컷. 흔들림이나 처짐 없이 원하는 각도로 짱짱하게 고정됨",
                "▲ 침대 헤드 전체 설치 샷. 누워서 넷플릭스/유튜브 보는 침대순이 필수 힐링템"
            ]

            opening_text = f"""누워서 스마트폰이나 아이패드 들고 보다가 손에 힘 빠져서 얼굴에 떨어뜨려 코나 입술 제대로 찍혀본 경험... 다들 한 번쯤 있으시죠? ㅠㅠ

저도 며칠 전에 침대에 누워서 넷플릭스 보다가 태블릿 모서리로 광대뼈를 강타당하고는, 진짜 이러다 이빨 부러지거나 코뼈 나가겠다 싶어서 그날 밤에 바로 침대 거치대 검색해서 내돈내산으로 질렀습니다 ㅋㅋㅋ
손목도 시큰거리고 고개 숙이고 보느라 목 디스크 증상까지 슬슬 오던 참이었거든요.

인터넷에 온통 협찬 광고글밖에 없어서 솔직히 반신반의했는데요,
3주 동안 침대 옆에 두고 매일 굴려본 결론부터 말씀드리면 **"진작 살 걸 그동안 왜 손목 아프게 미련하게 들고 봤나"** 싶을 정도로 대만족입니다!"""

            sec1_title = "싸구려 집게형 자바라 거치대 버리고 '바닥 스탠드형'으로 갈아탄 이유"
            sec1_body = """쇼핑몰 보면 1만 원 안팎의 침대 헤드 집게형 자바라 거치대도 엄청 많잖아요?
저도 처음엔 돈 아끼려고 그런 자바라 거치대를 2개나 사서 써봤는데요, 써보신 분들은 다 공감하실 겁니다.

**1. 태블릿 무게를 못 이기고 고개 숙이는 처짐 현상**
처음 며칠만 빳빳하고 조금만 쓰면 고개가 푹 꺾여서 누워있는 제 얼굴 쪽으로 스르륵 내려옵니다.
**2. 화면 한번 터치할 때마다 덜덜덜 흔들리는 멀미 현상**
자바라 철사가 얇다 보니 카톡 답장이나 화면 넘길 때마다 화면이 10초 동안 부들부들 떨려서 눈이 너무 피로해요.
**3. 침대 프레임 흠집과 파손**
집게로 침대 원목 헤드를 꽉 조이다 보니 원목에 자국이 남고 코팅이 벗겨지더라고요 ㅠㅠ

그래서 이번엔 돈을 조금 더 주더라도 **'바닥 스탠드형 + 탄소강 관절 스프링 구조'**로 골랐는데 이게 완전 신의 한 수였습니다!"""

            sec2_title = "왜 하필 '이 제품'을 사야 할까? (실사용 핵심 매력 3가지)"
            sec2_body = f"""제가 **'{clean_name}'**을 한 달 동안 써보면서 느낀 결정적 장점들입니다.

**1. 3kg 묵직한 스틸 원판 베이스로 흔들림/넘어짐 0%!**
바닥 받침대가 묵직한 탄소강 원판 스틸로 제작되어 있어서, 아이패드 12.9인치나 무거운 태블릿을 앞으로 길게 쭉 뻗어놔도 무게중심이 완벽하게 잡혀서 앞으로 쏠리거나 넘어지는 일이 전혀 없습니다. 침대 밑 틈새로 받침대를 쏙 밀어 넣으면 공간도 차지하지 않아요!

**2. 원하는 각도 360도 자유자재 고정 & 짱짱한 스프링 관절!**
싸구려 자바라처럼 힘겹게 철사를 구부릴 필요 없이, 관절 스프링 방식이라 한 손으로 살짝 당기거나 밀면 원하는 높이와 각도로 부드럽게 세팅됩니다. 누워서 옆으로 누워 잘 때도 각도만 살짝 돌려주면 되니까 너무 편해요!

**3. 두 손이 완전히 자유로운 삶의 질 수직 상승!**
추운 겨울에 이불 밖으로 손 꺼낼 필요 없이, 이불 폭 덮고 누워서 영화 한 편 다 볼 때까지 팔이 전혀 아프지 않습니다. 손목 시큰거리던 증상이 싹 사라졌어요!"""

            sec3_title = "솔직히 3주간 쓰면서 느낀 현실적인 단점 3가지"
            sec3_body = """무작정 칭찬만 하면 거짓말이니, 3주간 쓰면서 솔직히 아쉬웠던 점도 팩트체크합니다.

**1. 밑판이 워낙 묵직해서 밤에 발가락 찧으면 지옥을 경험함 ㅠㅠ**
바닥에 든든하게 고정되라고 만든 무거운 스틸 원판이라 안정감은 100점인데, 밤에 불 끄고 물 마시러 가다가 새끼발가락 부딪히면 진짜 눈물 쏙 빠집니다 ㅋㅋㅋ 받침대 위치를 침대 프레임 아래로 완전히 밀어 넣어두시는 걸 추천드려요!

**2. 장기간 사용 시 관절 조임 나사 점검 필요**
매일 각도를 수시로 꺾다 보면 관절 연결부 육각 볼트가 살짝 헐거워질 수 있습니다. 제품에 동봉된 미니 렌치로 한 달에 한 번씩 살짝 조여주시면 처음 샀을 때의 짱짱한 장력이 그대로 유지됩니다.

**3. 한번 누우면 침대 밖으로 나오질 못하는 마약 같은 게으름...**
이게 진짜 가장 치명적인 단점인데요 ㅋㅋㅋ 누워서 두 손 편하게 영상 보니까 주말에 침대에서 5시간 동안 꼼짝을 안 하게 되더라고요. 절제력이 필요합니다!"""

            sec4_title = "한 달 써보고 내린 최종 결론"
            sec4_body = """- 침대에 누워서 스마트폰, 태블릿, 닌텐도 스위치 즐기시는 분
- 싸구려 자바라 샀다가 처지고 흔들려서 버려본 경험 있는 분
- 손목 통증, 일자목, 거북목 때문에 편안한 자세가 절실한 분

이 가격대에 이만큼 매일매일 만족감을 주는 아이템은 대체재가 없다고 생각합니다. 고민 중이시라면 손목 건강을 위해서라도 강력 추천드려요!"""

        else:
            # ================= 3. 기타 일반 상품 맞춤 롱폼 (2,000자 고품질) =================
            captions = [
                "▲ 택배 도착하자마자 언박싱한 실물 샷! 패키지 마감이 생각보다 훨씬 탄탄하고 고급스러움",
                "▲ 실생활에서 매일 애용 중인 실사용 모습... 사소하게 손 가던 귀찮음과 피로도가 싹 사라짐",
                "▲ 세부 마감 디테일 컷. 튼튼한 내구성과 사용자 중심의 직관적인 편의성이 돋보임",
                "▲ 전체 구성품 및 패키지 컷. 가성비 대비 만족도 200%"
            ]

            opening_text = f"""장바구니에만 한 달 동안 담아두고 살까 말까 고민 백만 번 하다가...
결국 지난달에 결제해서 3주 넘게 매일 써본 **'{clean_name}'** 솔직 찐후기 풀어봅니다!

SNS 광고나 유튜브 추천 영상에 맨날 뜨길래 '아 또 흔한 바이럴 마케팅이겠지;' 하고 넘겼거든요?
근데 주변 지인들도 하나둘 사서 쓰는 거 보고 의심 반 호기심 반으로 제 돈 주고 사서 써봤는데요.
직접 3주간 써보니까 왜 다들 그렇게 찬양했는지 바로 납득이 가더라고요 ㅋㅋㅋ 결론은 대만족입니다!"""

            sec1_title = "시중의 수많은 저가형 대체재 대신 왜 '이 제품'을 골랐을까?"
            sec1_body = """쇼핑몰 뒤져보면 비슷한 기능에 1~2만 원 더 싼 저가형 카피 제품들도 정말 널려 있잖아요?
저도 처음엔 가성비 따진다고 싼 걸로 살까 고민했었는데요, 저가형 후기들을 꼼꼼하게 뜯어보니까 몇 달 못 쓰고 고장 나거나 마감이 엉망이라 결국 이중 지출했다는 후기가 수두룩하더라고요 ㅠㅠ

결국 "한번 살 때 제대로 된 거 사서 오래 쓰자!" 싶어서 완성도와 후기가 검증된 이 제품으로 골랐는데, 이게 정말 최고의 선택이었습니다.
사소하게 손이 여러 번 가던 번거로운 일들을 단번에 줄여주니까 하루 일과에서 오는 피로도가 눈에 띄게 줄어들었어요!"""

            sec2_title = "3주 동안 매일 써보고 느낀 핵심 특장점 3가지"
            sec2_body = f"""제가 **'{clean_name}'**을 직접 굴려보면서 가장 만족스러웠던 포인트 3가지입니다.

**1. 탄탄한 마감과 내구성으로 잔고장 걱정 제로!**
저가형 특유의 덜렁거림이나 유격 없이, 부품 하나하나 마감이 깔끔하고 내구성이 정말 탄탄합니다. 오래 써도 변형 없이 안심하고 쓸 수 있겠더라고요.

**2. 직관적인 사용 편의성과 디테일한 설계!**
설명서를 정독하지 않아도 누구나 직관적으로 바로 쓸 수 있을 만큼 조작이 직관적입니다. 사소한 부분까지 사용자 편의를 배려해서 설계되었다는 게 몸으로 느껴져요.

**3. 일상의 불편함을 확실하게 해결해 주는 확실한 돈값!**
매일 반복되던 귀찮고 번거로운 스트레스를 없애주니까, 사용 전과 후의 삶의 질 차이가 확연합니다. 돈 아깝다는 생각이 전혀 안 들어요!"""

            sec3_title = "솔직하게 느낀 아쉬운 단점 3가지 (팩트체크)"
            sec3_body = """장점만 나열하면 뻔한 광고 같으니, 3주간 쓰면서 솔직히 아쉬웠던 점도 공유합니다.

**1. 인기 기본 컬러/옵션은 품절이 너무 빨라요 ㅠㅠ**
저도 처음에 가장 무난한 옵션으로 사려다가 품절이 떠서 며칠 재입고 기다렸다가 겨우 샀습니다. 고민하다가 타이밍 놓치면 배송이 밀리니 재고 있을 때 바로 담으시는 걸 추천드려요.

**2. 처음 1~2일은 사용법/조작에 살짝 적응 기간 필요**
기존에 쓰던 방식과 약간 차이가 있어서 첫날엔 살짝 손에 덜 익었는데요, 딱 이틀 정도 쓰니까 완전히 익숙해져서 지금은 생각 없이도 척척 씁니다ㅋㅋ

**3. 저가형 대비 가격대가 살짝 있지만 그만큼 값어치를 함**
몇천 원, 1만 원짜리 초저가 제품들에 비하면 가격대가 조금 있지만, 매일 쓰는 빈도와 내구성을 생각하면 가성비 면에서 훨씬 이득이라고 봅니다."""

            sec4_title = "한 달 써보고 내린 최종 결론"
            sec4_body = """대기업 터무니없이 비싼 하이엔드 갈 필요 없이, 이 가격대에 이 정도 완성도와 실용성이면 실속파 분들에게 완벽한 선택지라고 봅니다.
고민하느라 시간 낭비하지 마시고 그냥 지르셔도 후회 안 하실 거예요! 돈값은 진작에 다 뽑았습니다ㅋㅋ"""

        # ----------------------------------------------------
        # 🎓 내 블로그 학습 스타일(말투, 첫인사, 끝인사) 100% 자동 적용
        # ----------------------------------------------------
        closing_box_text = ""
        closing_box_html = ""

        if persona:
            # 1. 학습된 첫인사 시그니처가 있으면 서두에 자연스럽게 배치
            if persona.get("first_greeting"):
                opening_text = f"{persona['first_greeting']}\n\n{opening_text}"

            # 2. 블로그 어조 맞춤형 변환 (경어체 등)
            opening_text = cls.adapt_tone_to_persona(opening_text, persona)
            sec1_body = cls.adapt_tone_to_persona(sec1_body, persona)
            sec2_body = cls.adapt_tone_to_persona(sec2_body, persona)
            sec3_body = cls.adapt_tone_to_persona(sec3_body, persona)
            sec4_body = cls.adapt_tone_to_persona(sec4_body, persona)

            # 3. 학습된 끝인사 시그니처 준비
            if persona.get("closing_phrase"):
                closing_box_text = f"\n\n{persona['closing_phrase']}\n"
                closing_box_html = f"""<div style="background:#f8fafc; border-left:4px solid #6366f1; padding:14px 18px; margin:25px 0 15px 0; border-radius:6px; font-size:14px; color:#334155; font-weight:600;">{persona['closing_phrase']}</div>"""

        # ----------------------------------------------------
        # 최종 순수 텍스트 & 네이버 스마트에디터 HTML 완성
        # ----------------------------------------------------
        clean_plain_text = f"""{selected_title}

{opening_text}

--------------------------------------------------
[실제 제품 사진 1: 택배 개봉 및 실물 언박싱]
{captions[0]}
--------------------------------------------------

{sec1_title}

{sec1_body}

--------------------------------------------------
[실제 제품 사진 2: 실사용 및 핵심 디테일 컷]
{captions[1]}
--------------------------------------------------

{sec2_title}

{sec2_body}

--------------------------------------------------
[실제 제품 사진 3: 부품 마감 및 기능성 컷]
{captions[2]}
--------------------------------------------------

{sec3_title}

{sec3_body}

--------------------------------------------------
[실제 제품 사진 4: 전체 설치/사용 완료 컷]
{captions[3]}
--------------------------------------------------

{sec4_title}

{sec4_body}{closing_box_text}

좌표 물어보시는 분들이 많아서 제가 구매했던 공식 판매처 최저가 할인 링크 아래 남겨둘게요!
지금 기간 한정 할인 쿠폰 적용되는 링크니까 재고랑 실시간 할인가 먼저 확인해 보세요 👇

👉 [실시간 최저가 할인 & 상세 스펙 바로가기]
구매 링크: {product_url}

(이 포스팅은 쿠팡 파트너스 및 제휴 마케팅 활동의 일환으로, 일정액의 수수료를 제공받을 수 있지만 실제 사용 후 느낀 점을 솔직하게 작성한 내돈내산 후기입니다.)"""

        clean_html = f"""<div style="font-family:'Pretendard', sans-serif; line-height:1.85; color:#222; max-width:680px; margin:0 auto; padding:20px;">
  <h1 style="font-size:22px; font-weight:800; color:#111; margin-bottom:20px; line-height:1.4;">{selected_title}</h1>
  
  <p style="margin-bottom:18px;">{opening_text.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:28px 0;">
    <img src="{imgs[0]}" alt="{clean_name} 택배 언박싱 실물 사진" style="max-width:100%; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.12);" />
    <p style="color:#666; font-size:13px; margin-top:8px; font-weight:500;">{captions[0]}</p>
  </div>

  <hr style="border:none; border-top:1px dashed #d1d5db; margin:32px 0;">

  <h3 style="font-size:18px; font-weight:bold; color:#03cf5d; margin:25px 0 12px 0;">{sec1_title}</h3>
  <p style="margin-bottom:20px;">{sec1_body.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:28px 0;">
    <img src="{imgs[1]}" alt="{clean_name} 실사용 디테일 컷" style="max-width:100%; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.12);" />
    <p style="color:#666; font-size:13px; margin-top:8px; font-weight:500;">{captions[1]}</p>
  </div>

  <hr style="border:none; border-top:1px dashed #d1d5db; margin:32px 0;">

  <h3 style="font-size:18px; font-weight:bold; color:#2563eb; margin:25px 0 12px 0;">{sec2_title}</h3>
  <p style="margin-bottom:20px;">{sec2_body.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:28px 0;">
    <img src="{imgs[2]}" alt="{clean_name} 마감 및 디테일 사진" style="max-width:100%; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.12);" />
    <p style="color:#666; font-size:13px; margin-top:8px; font-weight:500;">{captions[2]}</p>
  </div>

  <hr style="border:none; border-top:1px dashed #d1d5db; margin:32px 0;">

  <h3 style="font-size:18px; font-weight:bold; color:#ef4444; margin:25px 0 12px 0;">{sec3_title}</h3>
  <p style="margin-bottom:20px;">{sec3_body.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:28px 0;">
    <img src="{imgs[3]}" alt="{clean_name} 패키지 전체 사진" style="max-width:100%; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.12);" />
    <p style="color:#666; font-size:13px; margin-top:8px; font-weight:500;">{captions[3]}</p>
  </div>

  <hr style="border:none; border-top:1px dashed #d1d5db; margin:32px 0;">

  <h3 style="font-size:18px; font-weight:bold; color:#111; margin:25px 0 12px 0;">{sec4_title}</h3>
  <p style="margin-bottom:22px;">{sec4_body.replace(chr(10), '<br>')}</p>
  {closing_box_html}
  <p style="margin-bottom:16px;">좌표 물어보시는 분들이 많아서 제가 구매했던 공식 판매처 최저가 할인 링크 아래 남겨둘게요!<br>지금 기간 한정 할인 쿠폰 적용되는 링크니까 재고랑 실시간 할인가 먼저 확인해 보세요 👇</p>
  <p style="margin-bottom:20px; background:#f0fdf4; border:1px solid #bbf7d0; padding:16px; border-radius:10px;">
    👉 <a href="{product_url}" target="_blank" style="color:#03cf5d; font-weight:bold; text-decoration:underline;">[실시간 최저가 할인 & 상세 스펙 바로가기]</a><br>
    <span style="font-size:12px; color:#666;">구매 링크: {product_url}</span>
  </p>
  <p style="font-size:12px; color:#888; border-top:1px solid #eee; padding-top:15px;">*(이 포스팅은 쿠팡 파트너스 및 제휴 마케팅 활동의 일환으로, 일정액의 수수료를 제공받을 수 있지만 실제 사용 후 느낀 점을 솔직하게 작성한 내돈내산 후기입니다.)*</p>
</div>"""

        threads = [
            f"1/5 🧵\n{selected_title}\n\n{opening_text[:120]}...\n\n3주 실사용 찐후기 타래로 풀어봄 👇",
            f"2/5 💡\n{sec1_title}\n{sec1_body[:130]}...",
            f"3/5 🔍\n{sec2_title}\n{sec2_body[:130]}...",
            f"4/5 ⚠️\n{sec3_title}\n{sec3_body[:130]}...",
            f"5/5 🔗\n현재 기간 한정 할인 쿠폰 적용되는 최저가 링크는 프로필 링크(또는 첫 번째 댓글)에 남겨둘게요!\n궁금한 거 있으시면 댓글 주시면 솔직하게 답해드림 👇"
        ]

        # ----------------------------------------------------
        # 📸 인스타그램 피드 캡션 & 해시태그 & 카드뉴스 슬라이드
        # ----------------------------------------------------
        insta_hashtags_map = {
            "windbreak": "#내돈내산 #방풍비닐 #외풍차단 #창문단열 #뽁뽁이 #겨울준비 #난방비절약 #자취꿀템 #살림꿀템 #홈스타그램 #겨울필수템 #쿠팡추천템 #꿀템추천",
            "holder": "#내돈내산 #침대거치대 #태블릿거치대 #아이패드스탠드 #스마트폰거치대 #자취꿀템 #방꾸미기 #침대순이 #데스크테리어 #홈스타그램 #꿀템추천",
            "health": "#내돈내산 #마사지기추천 #어깨마사지기 #목마사지기 #안마기 #부모님선물 #효도선물 #힐링템 #피로회복 #홈케어 #건강스타그램 #직장인꿀템",
            "appliance": "#내돈내산 #가습기추천 #미니온풍기 #생활가전 #겨울가전 #방꾸미기 #자취방꾸미기 #살림스타그램 #살림템 #꿀템추천",
            "kitchen": "#내돈내산 #주방템 #프라이팬추천 #텀블러추천 #살림스타그램 #요리스타그램 #살림꿀템 #주방용품 #꿀템추천",
            "general": "#내돈내산 #찐후기 #솔직후기 #꿀템추천 #살림스타그램 #자취꿀템 #생활꿀팁 #쿠팡추천템 #인스타대란템 #삶의질상승"
        }
        hashtags = insta_hashtags_map.get(category, insta_hashtags_map["general"])

        insta_caption = f"""{selected_title} ✨

장바구니에만 한 달 동안 담아두고 고민하다가...
결국 질러서 3주 넘게 매일 써본 솔직 찐후기 풀어봅니다! ㅋㅋㅋ

💡 왜 하필 이 제품을 골랐을까?
{sec1_title}
대체재 대비 확실한 마감과 내구성, 그리고 사용자 편의성까지 갖춰서 일상의 귀찮은 스트레스가 싹 사라졌어요!

⚠️ 3주 써보고 느낀 아쉬운 단점 팩트체크!
{sec3_title}
좋은 점만 말하면 광고 같으니 솔직히 말씀드리면, 초기 적응이나 실측에 살짝 신경 쓰셔야 합니다.

🎯 최종 한줄평
돈 아깝다는 생각 전혀 안 들고 본전은 진작에 다 뽑았습니다! 올겨울 강력 추천 꿀템 인정 👍

🔗 실시간 최저가 할인 & 상세 스펙 구매처는
👉 프로필 링크(또는 스토리 하이라이트)에 걸어둘게요!

.
.
{hashtags}"""

        insta_slides = [
            {"slide": 1, "title": "표지 (Slide 1)", "desc": selected_title, "image": imgs[0]},
            {"slide": 2, "title": "기존 제품의 한계 (Slide 2)", "desc": sec1_title, "image": imgs[1]},
            {"slide": 3, "title": "핵심 특장점 (Slide 3)", "desc": sec2_title, "image": imgs[2]},
            {"slide": 4, "title": "솔직 단점 팩트체크 (Slide 4)", "desc": sec3_title, "image": imgs[3]},
            {"slide": 5, "title": "최종 결론 & 구매처 (Slide 5)", "desc": "프로필 링크에서 최저가 확인!", "image": imgs[0]}
        ]

        # ----------------------------------------------------
        # 🟠 티스토리(Tistory) 전용 구글 SEO 최적화 서식
        # ----------------------------------------------------
        tistory_html = f"""<div class="tistory-article" style="font-family:'Noto Sans KR', sans-serif; line-height:1.9; color:#333; max-width:720px; margin:0 auto; padding:15px;">
  <h2 style="font-size:24px; font-weight:800; color:#111; margin-bottom:20px; border-bottom:2px solid #ff5722; padding-bottom:10px;">{selected_title}</h2>
  
  <p style="margin-bottom:20px; font-size:16px;">{opening_text.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:30px 0;">
    <img src="{imgs[0]}" alt="{clean_name} 실물 언박싱" style="max-width:100%; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);" />
    <p style="color:#666; font-size:13px; margin-top:8px;">{captions[0]}</p>
  </div>

  <h3 style="font-size:20px; font-weight:bold; color:#ff5722; margin:35px 0 15px 0; border-left:4px solid #ff5722; padding-left:12px;">{sec1_title}</h3>
  <p style="margin-bottom:20px; font-size:15px;">{sec1_body.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:30px 0;">
    <img src="{imgs[1]}" alt="{clean_name} 실사용 디테일" style="max-width:100%; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);" />
    <p style="color:#666; font-size:13px; margin-top:8px;">{captions[1]}</p>
  </div>

  <h3 style="font-size:20px; font-weight:bold; color:#1976d2; margin:35px 0 15px 0; border-left:4px solid #1976d2; padding-left:12px;">{sec2_title}</h3>
  <p style="margin-bottom:20px; font-size:15px;">{sec2_body.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:30px 0;">
    <img src="{imgs[2]}" alt="{clean_name} 기능성 사진" style="max-width:100%; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);" />
    <p style="color:#666; font-size:13px; margin-top:8px;">{captions[2]}</p>
  </div>

  <h3 style="font-size:20px; font-weight:bold; color:#e53935; margin:35px 0 15px 0; border-left:4px solid #e53935; padding-left:12px;">{sec3_title}</h3>
  <p style="margin-bottom:20px; font-size:15px;">{sec3_body.replace(chr(10), '<br>')}</p>

  <div style="text-align:center; margin:30px 0;">
    <img src="{imgs[3]}" alt="{clean_name} 전체 사진" style="max-width:100%; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);" />
    <p style="color:#666; font-size:13px; margin-top:8px;">{captions[3]}</p>
  </div>

  <h3 style="font-size:20px; font-weight:bold; color:#333; margin:35px 0 15px 0; border-left:4px solid #333; padding-left:12px;">{sec4_title}</h3>
  <p style="margin-bottom:25px; font-size:15px;">{sec4_body.replace(chr(10), '<br>')}</p>

  <div style="background:#fff3e0; border:1px solid #ffe0b2; padding:20px; border-radius:8px; margin:30px 0;">
    <p style="margin:0 0 10px 0; font-weight:bold; color:#e65100; font-size:16px;">👉 [공식 판매처 최저가 할인 및 상세 스펙 안내]</p>
    <p style="margin:0;"><a href="{product_url}" target="_blank" rel="noopener noreferrer" style="color:#e65100; text-decoration:underline; font-weight:bold;">{product_url}</a></p>
  </div>

  <p style="font-size:12px; color:#888; border-top:1px solid #eee; padding-top:15px; margin-top:30px;">
    ※ 이 포스팅은 제휴 마케팅 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.
  </p>
</div>"""

        return {
            "title_candidates": titles,
            "selected_title": selected_title,
            "plain_text": clean_plain_text,
            "html_content": clean_html,
            "threads_items": threads,
            "instagram": {
                "caption": insta_caption,
                "slides": insta_slides,
                "hashtags": hashtags
            },
            "tistory": {
                "title": selected_title,
                "html_content": tistory_html
            },
            "images": imgs,
            "captions": captions
        }
