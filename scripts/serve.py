#!/usr/bin/env python3
"""dere — local server for a decision board.

Serves the board page and stores submitted answers as JSON. Binds to 127.0.0.1 only.

GET  /                 -> <dir>/board.html (the current board)
GET  /<name>.html      -> another page in <dir>
POST /submit           -> <answers>/<form_id>.json  (+ a timestamped copy)
GET  /answers/<form_id>-> the latest answers for that form

Usage:
  python3 serve.py --dir ./board --answers ./answers --port 8795
"""
import argparse, datetime, http.server, json, os, pathlib, re, urllib.parse

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default=".", help="folder that holds board.html")
ap.add_argument("--answers", default="./answers", help="folder for submitted answers")
ap.add_argument("--port", type=int, default=8795)
args = ap.parse_args()

ROOT = pathlib.Path(args.dir).resolve()
ANS = pathlib.Path(args.answers).resolve()
ANS.mkdir(parents=True, exist_ok=True)
SAFE = re.compile(r"[^\w.\-一-鿿]+")


def safe_name(s):
    return SAFE.sub("_", str(s))[:120] or "board"


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urllib.parse.unquote(self.path.split("?")[0])
        if p in ("/", "/index.html"):
            f = ROOT / "board.html"
            return self._send(200, f.read_bytes(), "text/html; charset=utf-8") if f.exists() else self._send(404, '{"error":"no board.html"}')
        if p.startswith("/answers/"):
            f = ANS / (safe_name(p[len("/answers/"):]) + ".json")
            return self._send(200, f.read_text("utf-8")) if f.exists() else self._send(404, "{}")
        name = p.lstrip("/")
        if name.endswith(".html") and "/" not in name and (ROOT / name).is_file():
            return self._send(200, (ROOT / name).read_bytes(), "text/html; charset=utf-8")
        return self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path.split("?")[0] != "/submit":
            return self._send(404, '{"error":"not found"}')
        n = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception as e:  # malformed JSON from the page
            return self._send(400, json.dumps({"error": str(e)}))
        now = datetime.datetime.now()
        data["_submitted_at"] = now.isoformat(timespec="seconds")
        name = safe_name(data.get("_form", "board"))
        txt = json.dumps(data, ensure_ascii=False, indent=2)
        (ANS / f"{name}.json").write_text(txt, "utf-8")
        (ANS / f"{name}_{now:%Y%m%d-%H%M%S}.json").write_text(txt, "utf-8")
        return self._send(200, json.dumps({"ok": True, "saved_at": data["_submitted_at"]}))

    def log_message(self, *a):
        pass


print(f"dere: serving {ROOT}/board.html on http://127.0.0.1:{args.port}/  (answers -> {ANS})")
http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
