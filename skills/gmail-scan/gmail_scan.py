#!/usr/bin/python3
"""Vigil Gmail scan: READ-ONLY IMAP through the sandbox proxy.
Prints recent, not-yet-processed emails as JSON. Never sends, deletes, or marks mail as read.
Config (never commit): /sandbox/.openclaw/vigil/gmail.json -> {"email", "app_password", "filter"}"""
import argparse, email, imaplib, json, os, re, socket
from email.header import decode_header, make_header
from pathlib import Path
from urllib.parse import urlparse

CFG = Path("/sandbox/.openclaw/vigil/gmail.json")
SEEN = Path("/sandbox/.openclaw/vigil/gmail_seen.json")

ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=2)
ap.add_argument("--max", type=int, default=15)
ap.add_argument("--all", action="store_true", help="include already-processed emails")
ap.add_argument("--no-mark", action="store_true", help="don't record emails as processed")
args = ap.parse_args()

proxy = urlparse(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "")

class ProxyIMAP(imaplib.IMAP4_SSL):
    """IMAP over TLS through the sandbox's HTTP CONNECT proxy (the sandbox has no direct internet)."""
    def _create_socket(self, timeout):
        s = socket.create_connection((proxy.hostname, proxy.port), timeout)
        s.sendall(f"CONNECT {self.host}:{self.port} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n\r\n".encode())
        r = b""
        while b"\r\n\r\n" not in r:
            c = s.recv(4096)
            if not c:
                break
            r += c
        first = r.split(b"\r\n")[0]
        if b" 200" not in first:
            raise OSError(f"proxy refused: {first!r}")
        return self.ssl_context.wrap_socket(s, server_hostname=self.host)

def body(msg):
    html = ""
    for p in (msg.walk() if msg.is_multipart() else [msg]):
        if p.get_content_disposition() == "attachment":
            continue
        ct = p.get_content_type()
        raw = p.get_payload(decode=True) if ct in ("text/plain", "text/html") else None
        if not raw:
            continue
        t = raw.decode(p.get_content_charset() or "utf-8", "replace")
        if ct == "text/plain":
            return t
        html = html or re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(style|script).*?</\1>", " ", t))
    return html

cfg = json.loads(CFG.read_text())
seen = json.loads(SEEN.read_text()) if SEEN.exists() else []

m = ProxyIMAP("imap.gmail.com", 993)
m.login(cfg["email"], cfg["app_password"])
m.select("INBOX", readonly=True)
_, data = m.search(None, "X-GM-RAW", f'"newer_than:{args.days}d {cfg.get("filter", "-category:promotions -category:social")}"')
ids = data[0].split()[-args.max:]

out = []
for i in reversed(ids):
    _, d = m.fetch(i, "(BODY.PEEK[])")
    msg = email.message_from_bytes(d[0][1])
    mid = msg.get("Message-ID") or i.decode()
    if mid in seen and not args.all:
        continue
    hdr = lambda k: str(make_header(decode_header(msg.get(k, ""))))
    out.append({"id": mid, "from": hdr("From"), "date": msg.get("Date", ""), "subject": hdr("Subject"),
                "text": " ".join(body(msg).split())[:1500],
                "attachments": [p.get_filename() for p in msg.walk() if p.get_filename()]})
m.logout()

if out and not args.no_mark:
    SEEN.write_text(json.dumps((seen + [e["id"] for e in out])[-500:]))
print(json.dumps({"new": len(out), "emails": out}, ensure_ascii=False, indent=1))