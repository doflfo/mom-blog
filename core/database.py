import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "affiliate.db")
try:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
except Exception:
    pass

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 설정 테이블 (API 키, 스타일 페르소나, 퍼블리싱 키 등)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)
        
        # 스타일 페르소나 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tone TEXT NOT NULL,
                description TEXT,
                signature_phrase TEXT,
                sample_text TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        
        # 작업 히스토리 (콘텐츠 생성 및 에이전트 대화 내역, 조회수/클릭수 추적)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                product_url TEXT,
                product_name TEXT,
                persona_name TEXT,
                blog_content TEXT,
                threads_content TEXT,
                review_feedback TEXT,
                review_score INTEGER,
                agent_logs TEXT,
                status TEXT DEFAULT 'completed',
                views INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                revision_count INTEGER DEFAULT 0,
                published_platforms TEXT,
                created_at TEXT
            )
        """)
        
        # 기존 테이블 컬럼 마이그레이션 (안전 처리)
        cursor.execute("PRAGMA table_info(content_history)")
        columns = [col[1] for col in cursor.fetchall()]
        if "views" not in columns:
            cursor.execute("ALTER TABLE content_history ADD COLUMN views INTEGER DEFAULT 0")
        if "clicks" not in columns:
            cursor.execute("ALTER TABLE content_history ADD COLUMN clicks INTEGER DEFAULT 0")
        if "revision_count" not in columns:
            cursor.execute("ALTER TABLE content_history ADD COLUMN revision_count INTEGER DEFAULT 0")
        
        conn.commit()
        _seed_default_data(conn)

def _seed_default_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personas")
    count = cursor.fetchone()[0]
    
    if count == 0:
        default_personas = [
            (
                "솔직 담백 내돈내산 리뷰어",
                "솔직하고 털털하며 진솔한 어조 ('~했음', '~하더라고요', 솔직한 단점 필수 언급)",
                "광고 같지 않고 실제 1~3달 동안 써본 사람처럼 단점과 장점을 명확히 짚어주는 실구매자 스타일",
                "\"솔직히 처음엔 반신반의했는데 써보니까 답 나왔습니다.\"",
                "내가 이거 사기 전까지 장바구니에만 한 달 동안 넣어뒀는데, 결론부터 말하면 진작 살 걸 그랬음. 특히 소음 부분 걱정 많았는데 실사용 기준 거의 안 들림. 단점 하나 꼽자면 충전선 길이가 좀 짧은 게 아쉬움.",
                1,
                datetime.now().isoformat()
            ),
            (
                "친절한 테크/생활 꿀팁 전문가",
                "친근하고 배려심 깊은 경어체 ('~해요!', '도움이 되셨으면 좋겠습니다')",
                "핵심 스펙과 가성비, 그리고 놓치기 쉬운 사용 꿀팁을 정리해주는 친절한 가이드형 스타일",
                "\"오늘도 여러분의 현명한 소비를 돕는 리뷰 요정입니다!\"",
                "안녕하세요 여러분! 오늘은 요즘 SNS에서 핫한 바로 그 아이템을 가져왔어요. 스펙만 보면 감이 잘 안 오실 텐데, 기존 제품 대비 어떤 점이 개선되었는지 핵심만 3가지로 콕 짚어드릴게요!",
                0,
                datetime.now().isoformat()
            ),
            (
                "핵심요약 팩트폭격 가성비 헌터",
                "간결하고 스피디한 어조 ('3줄 요약', 불필요한 미사여구 제거)",
                "바쁜 현대인을 위해 결론부터 던지고 최저가와 가성비 기준을 날카롭게 비교하는 스타일",
                "\"시간 없으신 분들을 위해 결론부터 3줄 요약 박고 갑니다.\"",
                "긴 말 필요 없이 결론부터 말씀드립니다. 1) 가격 대비 마감 우수 2) 배터리 타임 준수 3) 단, A/S는 감안 필요. 동급 타사 대비 30% 저렴해서 이 가격대엔 대체재가 없습니다.",
                0,
                datetime.now().isoformat()
            )
        ]
        
        cursor.executemany("""
            INSERT INTO personas (name, tone, description, signature_phrase, sample_text, is_default, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_personas)
        
        # 기본 설정값
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value, updated_at)
            VALUES ('llm_provider', 'auto', ?)
        """, (datetime.now().isoformat(),))
        
        conn.commit()

def get_settings():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return dict(cursor.fetchall())

def set_setting(key, value):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """, (key, value, datetime.now().isoformat()))
        conn.commit()

def get_personas():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas ORDER BY is_default DESC, id ASC")
        return [dict(row) for row in cursor.fetchall()]

def get_persona(persona_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE id = ?", (persona_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def save_persona(name, tone, description, signature_phrase, sample_text):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO personas (name, tone, description, signature_phrase, sample_text, is_default, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (name, tone, description, signature_phrase, sample_text, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid

def save_history(title, product_url, product_name, persona_name, blog_content, threads_content, review_feedback, review_score, agent_logs):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO content_history 
            (title, product_url, product_name, persona_name, blog_content, threads_content, review_feedback, review_score, agent_logs, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)
        """, (
            title, product_url, product_name, persona_name, 
            blog_content, 
            json.dumps(threads_content, ensure_ascii=False) if isinstance(threads_content, (list, dict)) else str(threads_content),
            json.dumps(review_feedback, ensure_ascii=False) if isinstance(review_feedback, (list, dict)) else str(review_feedback),
            review_score,
            json.dumps(agent_logs, ensure_ascii=False) if isinstance(agent_logs, (list, dict)) else str(agent_logs),
            datetime.now().isoformat()
        ))
        conn.commit()
        return cursor.lastrowid

def update_stats(history_id: int, views: int, clicks: int):
    """실제 포스팅의 조회수 및 클릭수 기록"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE content_history
            SET views = ?, clicks = ?
            WHERE id = ?
        """, (views, clicks, history_id))
        conn.commit()

def update_revised_content(history_id: int, new_title: str, new_blog_content: str, new_threads_content: any, review_feedback: any, score: int):
    """클릭수 저조 시 긴급 수정본(A/B Rescue) 업데이트"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE content_history
            SET title = ?,
                blog_content = ?,
                threads_content = ?,
                review_feedback = ?,
                review_score = ?,
                revision_count = revision_count + 1
            WHERE id = ?
        """, (
            new_title,
            new_blog_content,
            json.dumps(new_threads_content, ensure_ascii=False) if isinstance(new_threads_content, (list, dict)) else str(new_threads_content),
            json.dumps(review_feedback, ensure_ascii=False) if isinstance(review_feedback, (list, dict)) else str(review_feedback),
            score,
            history_id
        ))
        conn.commit()

def get_history(limit=30):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, product_name, persona_name, review_score, views, clicks, revision_count, created_at, status FROM content_history ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_history_detail(history_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content_history WHERE id = ?", (history_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        try:
            data['threads_content'] = json.loads(data['threads_content'])
        except Exception:
            pass
        try:
            data['review_feedback'] = json.loads(data['review_feedback'])
        except Exception:
            pass
        try:
            data['agent_logs'] = json.loads(data['agent_logs'])
        except Exception:
            pass
        return data

def get_learned_blog_profile():
    """사용자가 연동한 블로그에서 학습한 맞춤 스타일 프로필 조회"""
    settings = get_settings()
    raw = settings.get("learned_blog_profile")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None

def save_learned_blog_profile(profile_dict: dict):
    """블로그 학습 프로필 저장 (다음 글부터 100% 자동 반영)"""
    set_setting("learned_blog_profile", json.dumps(profile_dict, ensure_ascii=False))

# 모듈 로드 시 안전한 DB 및 테이블 자동 생성
try:
    init_db()
except Exception:
    pass
