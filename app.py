import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import threading
from core.database import (
    init_db, get_personas, get_persona, save_persona,
    get_settings, set_setting, get_history, get_history_detail,
    get_learned_blog_profile, save_learned_blog_profile
)
from core.blog_learner import BlogStyleLearner
from agents.orchestrator import AffiliateStudioOrchestrator
from agents.publisher import PublisherAgent

# 클라우드 호스팅(Render, Koyeb 등) 및 로컬 환경 자동 포트 바인딩
PORT = int(os.environ.get("PORT", 8999))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# 오케스트레이터 싱글톤
orchestrator = AffiliateStudioOrchestrator()
publisher = PublisherAgent()

class StudioAPIHandler(http.server.SimpleHTTPRequestHandler):
    """
    내장 HTTP 서버 기반 풀스택 REST API 및 대시보드 서빙 핸들러
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            with open(os.path.join(STATIC_DIR, "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        if path.startswith("/api/"):
            self._handle_api_get(path, query)
            return

        # 일반 정적 파일 서빙
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                body_json = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
            except Exception:
                body_json = {}

            self._handle_api_post(path, body_json)
            return

        self._send_json({"error": "Not Found"}, status=404)

    def _handle_api_get(self, path, query):
        if path == "/api/personas":
            personas = get_personas()
            self._send_json({"success": True, "personas": personas})
        elif path == "/api/settings":
            settings = get_settings()
            # 민감 정보 마스킹 처리(앞자리만 노출)
            safe_settings = {}
            for k, v in settings.items():
                if "key" in k or "password" in k or "token" in k:
                    safe_settings[k] = v[:4] + "****" if len(v) > 4 else ("****" if v else "")
                else:
                    safe_settings[k] = v
            self._send_json({"success": True, "settings": safe_settings})
        elif path == "/api/history":
            history = get_history(limit=20)
            self._send_json({"success": True, "history": history})
        elif path == "/api/learned-blog":
            profile = get_learned_blog_profile()
            self._send_json({"success": True, "profile": profile})
        elif path.startswith("/api/history/"):
            try:
                hid = int(path.split("/")[-1])
                detail = get_history_detail(hid)
                if detail:
                    self._send_json({"success": True, "detail": detail})
                else:
                    self._send_json({"success": False, "message": "History not found"}, status=404)
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, status=400)
        else:
            self._send_json({"error": "Unknown API endpoint"}, status=404)

    def _handle_api_post(self, path, body):
        if path == "/api/generate":
            # 멀티 에이전트 생성 파이프라인 가동
            product_url = body.get("product_url", "").strip()
            product_text = body.get("product_text", "").strip()
            benchmark_text = body.get("benchmark_text", "").strip()
            custom_image = body.get("custom_image", "").strip()
            persona_id = int(body.get("persona_id", 1))

            try:
                result = orchestrator.run_pipeline(
                    product_url=product_url,
                    product_text=product_text,
                    benchmark_text=benchmark_text,
                    custom_image=custom_image,
                    persona_id=persona_id
                )
                self._send_json({"success": True, "result": result})
            except Exception as e:
                import traceback
                traceback.print_exc()
                self._send_json({"success": False, "message": f"생성 오류: {str(e)}"}, status=200)

        elif path == "/api/personas":
            # 신규 페르소나 생성
            name = body.get("name", "").strip()
            tone = body.get("tone", "").strip()
            desc = body.get("description", "").strip()
            sig = body.get("signature_phrase", "").strip()
            sample = body.get("sample_text", "").strip()

            if not (name and tone):
                self._send_json({"success": False, "message": "페르소나 이름과 말투는 필수입니다."}, status=400)
                return

            new_id = save_persona(name, tone, desc, sig, sample)
            self._send_json({"success": True, "id": new_id, "message": "새로운 스타일 페르소나가 등록되었습니다."})

        elif path == "/api/settings":
            for k, v in body.items():
                if v and not v.endswith("****"):  # 마스킹되지 않은 실제 입력값만 저장
                    set_setting(k, v)
            self._send_json({"success": True, "message": "설정이 성공적으로 저장되었습니다."})

        elif path == "/api/history/update-stats":
            hid = int(body.get("history_id", 0))
            views = int(body.get("views", 0))
            clicks = int(body.get("clicks", 0))
            from core.database import update_stats
            update_stats(hid, views, clicks)
            self._send_json({"success": True, "message": "성과 지표가 업데이트되었습니다."})

        elif path == "/api/history/revise-low-clicks":
            hid = int(body.get("history_id", 0))
            views = int(body.get("views", 0))
            clicks = int(body.get("clicks", 0))
            try:
                res = orchestrator.revise_for_low_clicks(hid, views, clicks)
                self._send_json({"success": True, "result": res, "message": "클릭률을 극대화하는 긴급 A/B 테스트 개정본이 완성되었습니다!"})
            except Exception as e:
                self._send_json({"success": False, "message": f"수정 실패: {str(e)}"}, status=500)

        elif path == "/api/publish/wordpress":
            title = body.get("title", "")
            content = body.get("content", "")
            status = body.get("status", "draft")
            res = publisher.publish_to_wordpress(title, content, status=status)
            self._send_json(res)

        elif path == "/api/publish/tistory":
            title = body.get("title", "")
            content = body.get("content", "")
            res = publisher.publish_to_tistory(title, content)
            self._send_json(res)

        elif path == "/api/learn-blog":
            blog_url = body.get("blog_url", "").strip()
            try:
                profile = BlogStyleLearner.analyze_published_blog(blog_url)
                save_learned_blog_profile(profile)
                self._send_json({
                    "success": True,
                    "profile": profile,
                    "message": "🎉 내 블로그 스타일 학습 완료! 다음 글부터 이 블로그에 맞춰 자동으로 업그레이드되어 작성됩니다."
                })
            except Exception as e:
                self._send_json({"success": False, "message": f"학습 실패: {str(e)}"}, status=200)

        else:
            self._send_json({"error": "Unknown POST endpoint"}, status=404)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

def run_server(port=PORT):
    # 콘솔 utf-8 인코딩 대응
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
        # 화면(모니터)은 꺼져도 시스템(CPU/네트워크)이 절전 모드에 빠지지 않도록 24시간 가동 유지
        try:
            import ctypes
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ES_AWAYMODE_REQUIRED = 0x00000040
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
            print("[절전 방지 모드 활성화] 모니터는 꺼져도 서버와 터널은 24시간 멈추지 않습니다.")
        except Exception as e:
            print(f"[절전 방지 모드 경고]: {e}")

    init_db()
    server_address = ('0.0.0.0', port)
    
    # 포트 충돌 방지 및 재사용 허용
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, StudioAPIHandler) as httpd:
        print("=" * 64)
        print(f"[AutoAffiliate Studio] AI 수익화 자동화 오피스 가동 중!")
        print(f"브라우저 접속 주소: http://127.0.0.1:{port}")
        print("=" * 64)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")
            httpd.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
