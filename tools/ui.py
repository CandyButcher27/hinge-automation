import argparse
import ast
import json
import queue
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import hinge

PAGE = Path(__file__).with_name("ui.html")
lock = threading.Lock()
answers = queue.Queue()
stop = threading.Event()
state = {"running": False, "pending": None, "log": [], "cap": 5}


def say(msg):
    with lock:
        state["log"] = (state["log"] + [f"{time.strftime('%H:%M:%S')}  {msg}"])[-200:]


def pending(question):
    if question.startswith("comment: "):
        return {"kind": "comment", "suggestion": ast.literal_eval(question[9:question.rindex(" - enter")])}
    return {"kind": "decide", "question": question.removesuffix(" [y/n/q] ")}


def ask(question):
    with lock:
        state["pending"] = pending(question)
    answer = "q" if stop.is_set() else answers.get()
    with lock:
        state["pending"] = None
    say(f"answer: {answer or 'keep the comment'}")
    return answer


def start(opts):
    with lock:
        if state["running"]:
            return
        state.update(running=True, cap=int(opts["cap"]))
    stop.clear()
    while not answers.empty():
        answers.get_nowait()

    def work():
        try:
            hinge.run(int(opts["cap"]), opts["source"], bool(opts["full"]), bool(opts["auto"]), opts["provider"],
                      ask=ask, say=say, stopped=stop.is_set)
        except hinge.Stop as e:
            say(f"stopped: {e}")
        except Exception as e:
            say(f"error: {e!r}")
        finally:
            with lock:
                state.update(running=False, pending=None)
            say("run ended")

    threading.Thread(target=work, daemon=True).start()


def prompts_error(text):
    for line in text.splitlines():
        if line.strip() and not (line.strip().isascii() and line.strip().isprintable()):
            return f"not printable ASCII: {line.strip()!r}"
    return None


class Handler(BaseHTTPRequestHandler):
    def reply(self, body, kind="application/json", code=200):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.reply(PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path.startswith("/frame.png"):
            try:
                self.reply(hinge.screen(), "image/png")
            except Exception as e:
                self.reply({"error": str(e)}, code=503)
        elif self.path == "/state":
            with lock:
                self.reply({**state, "today": hinge.liked_today()})
        elif self.path == "/prompts":
            self.reply({"text": hinge.COMMENTS.read_text(encoding="utf-8")})
        else:
            self.reply({"error": "not found"}, code=404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/start":
            start(body)
        elif self.path == "/answer":
            answers.put(str(body.get("answer", "")))
        elif self.path == "/stop":
            stop.set()
            answers.put("q")
        elif self.path == "/prompts":
            error = prompts_error(body.get("text", ""))
            if error:
                return self.reply({"error": error}, code=400)
            hinge.COMMENTS.write_text(body["text"].strip() + "\n", encoding="utf-8")
        else:
            return self.reply({"error": "not found"}, code=404)
        self.reply({"ok": True})

    def log_message(self, *args):
        pass


def main():
    p = argparse.ArgumentParser(description="Local web front end for hinge.py run")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true")
    a = p.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    url = f"http://127.0.0.1:{a.port}/"
    print(f"hinge ui on {url} - ctrl+c to quit", flush=True)
    if not a.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop.set()
        answers.put("q")


if __name__ == "__main__":
    main()
