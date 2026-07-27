#!/usr/bin/env python3
"""
Daily Combined Telegraph Digest.

Runs the existing digest producer scripts, extracts text from their PDFs,
and publishes the result as a Telegraph page. Prints the Telegraph link.

Standalone — needs only Python 3.10+ stdlib.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

USER_SITE = "/opt/data/home/.local/lib/python3.13/site-packages"
if USER_SITE not in sys.path:
    sys.path.insert(0, USER_SITE)

from pypdf import PdfReader

ROOT = Path("/opt/data")
SCRIPTS = ROOT / "scripts"
OUT_DIR = ROOT / "home/.cron/output/daily-telegraph-digest"
STATE_DIR = ROOT / "home/.cron/state"
STATE_FILE = STATE_DIR / "daily-telegraph-digest.json"
ACCOUNT_TOKEN_FILE = STATE_DIR / "telegraph_account_token.txt"

PRODUCERS = [
    {
        "name": "All-Tech PDF Digest",
        "cmd": [sys.executable, str(SCRIPTS / "all-tech-pdf-digest.py")],
    },
    {
        "name": "KareKeep Daily Bookmark PDF",
        "cmd": [sys.executable, str(SCRIPTS / "karekeep-daily-bookmark-pdf.py"), "--max-items", "80"],
    },
]

MEDIA_RE = re.compile(r"MEDIA:(/[^\s]+\.pdf)\b")
TELEGRAPH_API = "https://api.telegra.ph"


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(STATE_FILE)


def get_or_create_account() -> str:
    """Get existing Telegraph access token or create a new account."""
    if ACCOUNT_TOKEN_FILE.exists():
        token = ACCOUNT_TOKEN_FILE.read_text().strip()
        if token:
            return token
    # Create new Telegraph account
    url = f"{TELEGRAPH_API}/createAccount?short_name=Hermes%20Digest&author_name=Hermes%20Digest"
    try:
        resp = json.loads(urllib.request.urlopen(url, timeout=15).read().decode())
        if resp.get("ok") and resp.get("result", {}).get("access_token"):
            token = resp["result"]["access_token"]
            ACCOUNT_TOKEN_FILE.write_text(token)
            return token
    except Exception as exc:
        print(f"[telegraph] account creation failed: {exc}", file=sys.stderr)
    return ""


def run_producer(name: str, cmd: list[str]) -> list[Path]:
    """Run a producer script and return list of PDF paths it generated."""
    print(f"[telegraph] running {name}...", file=sys.stderr)
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=600)
    except subprocess.TimeoutExpired:
        print(f"[telegraph] {name} timed out", file=sys.stderr)
        return []

    output = proc.stdout or ""
    if proc.returncode != 0:
        print(f"[telegraph] {name} failed (code {proc.returncode})", file=sys.stderr)
        return []

    pdfs: list[Path] = []
    for match in MEDIA_RE.finditer(output):
        path = Path(match.group(1))
        if path.exists() and path.stat().st_size > 0:
            pdfs.append(path)
    return pdfs


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract readable text from a PDF."""
    try:
        reader = PdfReader(str(pdf_path))
        parts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                parts.append(text)
        return "\n\n".join(parts)
    except Exception as exc:
        print(f"[telegraph] pdf extraction failed for {pdf_path.name}: {exc}", file=sys.stderr)
        return ""


def text_to_telegraph_nodes(text: str) -> list:
    """Convert plain text into Telegraph API Node elements (simple paragraphs)."""
    nodes = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Bold headers (lines that look like headings)
        if re.match(r"^[A-Z][A-Za-z\s/]{2,50}:$", line) or re.match(r"^#+\s", line):
            clean = re.sub(r"^#+\s*", "", line).rstrip(":").strip()
            nodes.append({"tag": "h3", "children": [clean]})
        elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
            nodes.append({"tag": "p", "children": [line]})
        elif re.match(r"^https?://", line):
            nodes.append({"tag": "p", "children": [{"tag": "a", "attrs": {"href": line}, "children": [line[:80] + ("..." if len(line) > 80 else "")]}]})
        else:
            nodes.append({"tag": "p", "children": [line]})
    return nodes


def publish_to_telegraph(token: str, title: str, content_nodes: list, today_str: str) -> str | None:
    """Publish a page to Telegraph. Returns the URL or None."""
    content_json = json.dumps(content_nodes, ensure_ascii=False)
    data = urllib.parse.urlencode({
        "access_token": token,
        "title": title,
        "author_name": "Hermes Daily Digest",
        "content": content_json,
    }).encode()
    url = f"{TELEGRAPH_API}/createPage"
    try:
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        if resp.get("ok") and resp.get("result", {}).get("url"):
            return resp["result"]["url"]
        print(f"[telegraph] API error: {resp}", file=sys.stderr)
    except Exception as exc:
        print(f"[telegraph] publish failed: {exc}", file=sys.stderr)
    return None


def main() -> int:
    force = "--force" in sys.argv
    day = dt.datetime.now(dt.UTC).date().isoformat()
    state = load_state()

    if not force and state.get("last_sent_date") == day:
        print("[SILENT] already sent today")
        return 0

    # Get or create Telegraph account
    token = get_or_create_account()
    if not token:
        print("[telegraph] no access token available", file=sys.stderr)
        return 1

    # Run producers and collect PDFs
    all_pdfs: list[Path] = []
    for producer in PRODUCERS:
        all_pdfs.extend(run_producer(producer["name"], producer["cmd"]))

    # Deduplicate
    seen: set[str] = set()
    unique_pdfs: list[Path] = []
    for pdf in all_pdfs:
        key = str(pdf.resolve())
        if key not in seen:
            seen.add(key)
            unique_pdfs.append(pdf)

    if not unique_pdfs:
        print("[SILENT] no content produced today")
        return 0

    # Extract text from all PDFs
    today_str = dt.datetime.now(dt.UTC).strftime("%B %d, %Y")
    all_content = []
    for pdf in unique_pdfs:
        text = extract_text_from_pdf(pdf)
        if text:
            section_title = f"📄 {pdf.stem.replace('-', ' ').title()}"
            all_content.append({"tag": "h2", "children": [section_title]})
            all_content.extend(text_to_telegraph_nodes(text))
            all_content.append({"tag": "hr", "children": []})

    if not all_content:
        print("[SILENT] no extractable content from PDFs")
        return 0

    title = f"Daily Digest — {today_str}"

    # Publish to Telegraph (split into sections if too long)
    max_nodes_per_page = 60
    if len(all_content) <= max_nodes_per_page:
        url = publish_to_telegraph(token, title, all_content, today_str)
        if url:
            state.update({
                "last_sent_date": day,
                "last_sent_at_utc": dt.datetime.now(dt.UTC).isoformat(),
                "last_url": url,
                "source_pdfs": [str(p) for p in unique_pdfs],
            })
            save_state(state)
            print(f"🌐 {url}")
            return 0

    # Split into multiple pages if content is too long
    page_num = 1
    first_url = None
    for i in range(0, len(all_content), max_nodes_per_page):
        chunk = all_content[i:i + max_nodes_per_page]
        page_title = f"{title} (Part {page_num})" if page_num > 1 else title
        url = publish_to_telegraph(token, page_title, chunk, today_str)
        if url and not first_url:
            first_url = url
        page_num += 1

    if first_url:
        state.update({
            "last_sent_date": day,
            "last_sent_at_utc": dt.datetime.now(dt.UTC).isoformat(),
            "last_url": first_url,
            "total_pages": page_num - 1,
        })
        save_state(state)
        print(f"🌐 {first_url}")
        return 0

    print("[telegraph] failed to publish any pages", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
