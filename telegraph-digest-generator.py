#!/usr/bin/env python3
"""
Daily Combined Telegraph Digest — Rich Formatting with Images.

Imports data-collection functions from the existing producer scripts and
publishes beautifully formatted content to Telegraph with images, links,
and proper visual hierarchy.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

USER_SITE = "/opt/data/home/.local/lib/python3.13/site-packages"
if USER_SITE not in sys.path:
    sys.path.insert(0, USER_SITE)

SCRIPTS_DIR = Path("/opt/data/scripts")
OUT_DIR = Path("/opt/data/home/.cron/output/daily-telegraph-digest")
STATE_DIR = Path("/opt/data/home/.cron/state")
STATE_FILE = STATE_DIR / "daily-telegraph-digest.json"
TOKEN_FILE = STATE_DIR / "telegraph_account_token.txt"
TELEGRAPH_API = "https://api.telegra.ph"


# ═══════════════════════════════════════════════════════════════
# 1. Import data from producer scripts
# ═══════════════════════════════════════════════════════════════

def load_producer_module(name: str, path: Path):
    """Dynamically import a producer script as a Python module."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        # Make sys.stdout/stderr available to the producer
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod
    return None


def collect_tech_items():
    """Collect items from the All-Tech PDF Digest producer."""
    try:
        mod = load_producer_module("all_tech_digest", SCRIPTS_DIR / "all-tech-pdf-digest.py")
        if mod and hasattr(mod, "collect"):
            sections, statuses = mod.collect()
            return sections, statuses
    except Exception as e:
        print(f"[telegraph] all-tech import failed: {e}", file=sys.stderr)
    return {}, {}


def collect_bookmark_items():
    """Collect items from KareKeep bookmark producer (brief text summary)."""
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "karekeep-daily-bookmark-pdf.py"),
             "--max-items", "80", "--text-only"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=300)
        output = result.stdout or ""
        lines = [l.strip() for l in output.split("\n") if l.strip()]
        return lines
    except Exception as e:
        print(f"[telegraph] bookmark fetch failed: {e}", file=sys.stderr)
    return []


# ═══════════════════════════════════════════════════════════════
# 2. Telegraph API helpers
# ═══════════════════════════════════════════════════════════════

def get_or_create_token() -> str:
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
        if token:
            return token
    url = f"{TELEGRAPH_API}/createAccount?short_name=Hermes%20Daily&author_name=Hermes%20Daily%20Digest"
    try:
        resp = json.loads(urllib.request.urlopen(url, timeout=15).read().decode())
        if resp.get("ok"):
            token = resp["result"]["access_token"]
            TOKEN_FILE.write_text(token)
            return token
    except Exception as e:
        print(f"[telegraph] account creation: {e}", file=sys.stderr)
    return ""


def esc_text(text: str) -> str:
    """Escape text for Telegraph content (it uses HTML-like escaping)."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def text_node(text: str) -> dict | str:
    """Create a text node. Returns the string directly if plain text."""
    return esc_text(text)


def link_node(text: str, url: str) -> dict:
    return {"tag": "a", "attrs": {"href": url}, "children": [esc_text(text)]}


def bold_node(text: str) -> dict:
    return {"tag": "b", "children": [esc_text(text)]}


def paragraph_node(children: list) -> dict:
    return {"tag": "p", "children": children}


def heading_node(text: str, level: int = 3) -> dict:
    return {"tag": f"h{level}", "children": [esc_text(text)]}


def img_node(src: str) -> dict:
    return {"tag": "img", "attrs": {"src": src}}


def hr_node() -> dict:
    return {"tag": "hr", "children": []}


# ═══════════════════════════════════════════════════════════════
# 3. Build Telegraph content from items
# ═══════════════════════════════════════════════════════════════

def build_tech_section(sections: dict) -> list:
    """Convert all-tech items into Telegraph nodes with images."""
    nodes = []
    section_colors = ["#1B365D", "#2E7D5A", "#8B4513", "#6B4C7A", "#B4653C"]

    for idx, (section_name, items) in enumerate(sections.items()):
        if not items:
            continue

        color = section_colors[idx % len(section_colors)]
        nodes.append(heading_node(f"📰 {section_name}", 2))
        nodes.append(hr_node())

        for item in items[:8]:  # Max 8 per section
            item_nodes = []

            # Title as a link
            title_text = esc_text(item.title)
            title_link = link_node(item.title, item.url)
            item_nodes.append(paragraph_node([
                {"tag": "b", "children": [title_link]}
            ]))

            # Meta line
            meta_parts = []
            if item.source:
                meta_parts.append(esc_text(f"[{item.source}]"))
            if item.author:
                meta_parts.append(esc_text(f"by {item.author}"))
            if item.score:
                meta_parts.append(esc_text(f"⚡{item.score}"))
            if meta_parts:
                item_nodes.append(paragraph_node([
                    {"tag": "i", "children": [" · ".join(meta_parts)]}
                ]))

            # Thumbnail — use external URL directly (Telegraph supports this)
            if item.thumbnail and item.thumbnail.startswith(("http://", "https://")):
                item_nodes.append(img_node(item.thumbnail))

            # Summary
            if item.summary:
                summary = item.summary[:600]
                item_nodes.append(paragraph_node([esc_text(summary)]))

            # Why it matters
            why = why_it_matters(item)
            if why:
                item_nodes.append(paragraph_node([
                    {"tag": "b", "children": [esc_text("💡 Why it matters: ")]},
                    esc_text(why)
                ]))

            nodes.extend(item_nodes)
            nodes.append(hr_node())

    return nodes


def build_bookmark_section(bookmark_lines: list) -> list:
    """Convert bookmark lines into Telegraph nodes."""
    if not bookmark_lines:
        return []
    nodes = [heading_node("🔖 KareKeep Bookmarks", 2), hr_node()]
    for line in bookmark_lines[:20]:
        if line.startswith("http"):
            nodes.append(paragraph_node([link_node(line[:80], line)]))
        else:
            nodes.append(paragraph_node([esc_text(line[:200])]))
    return nodes


def why_it_matters(item) -> str:
    """Generate a 'why it matters' note based on content signals."""
    text = (item.title + " " + (item.summary or "")).lower()
    signals = []
    if any(w in text for w in ["ai", "llm", "model", "agent", "coding", "developer"]):
        signals.append("AI/tooling signal")
    if any(w in text for w in ["gpu", "chip", "nvidia", "semiconductor", "hardware"]):
        signals.append("hardware signal")
    if any(w in text for w in ["security", "privacy", "breach", "vulnerability"]):
        signals.append("security signal")
    if any(w in text for w in ["startup", "funding", "apple", "microsoft", "meta"]):
        signals.append("industry signal")
    if any(w in text for w in ["nasa", "space", "satellite", "rocket"]):
        signals.append("space signal")
    if signals:
        return f"likely affects coding workflows, local models, or automation choices. ({', '.join(signals)})"
    return ""


# ═══════════════════════════════════════════════════════════════
# 4. Main
# ═══════════════════════════════════════════════════════════════

def main() -> int:
    force = "--force" in sys.argv
    day = dt.datetime.now(dt.UTC).date().isoformat()
    state = {}
    try:
        state = json.loads(STATE_FILE.read_text())
    except Exception:
        pass

    if not force and state.get("last_sent_date") == day:
        print("[SILENT] already sent today")
        return 0

    token = get_or_create_token()
    if not token:
        print("[telegraph] no access token", file=sys.stderr)
        return 1

    # Collect content from both producers
    all_nodes = []
    tech_sections, tech_statuses = collect_tech_items()
    if tech_sections:
        all_nodes.extend(build_tech_section(tech_sections))

    bookmark_lines = collect_bookmark_items()
    if bookmark_lines:
        all_nodes.extend(build_bookmark_section(bookmark_lines))

    if not all_nodes:
        print("[SILENT] no content collected")
        return 0

    # Add footer
    today_str = dt.datetime.now(dt.UTC).strftime("%B %d, %Y")
    all_nodes.append(heading_node("📡 Source Status", 3))
    all_nodes.append(paragraph_node([esc_text(str(tech_statuses))]))
    all_nodes.append(paragraph_node([
        {"tag": "i", "children": [esc_text(f"Generated by Hermes Daily Digest · {today_str}")]}
    ]))

    title = f"Daily Digest — {today_str}"

    # Publish to Telegraph
    content_json = json.dumps(all_nodes, ensure_ascii=False)
    data = urllib.parse.urlencode({
        "access_token": token,
        "title": title,
        "author_name": "Hermes Daily Digest",
        "content": content_json,
    }).encode()

    try:
        req = urllib.request.Request(
            f"{TELEGRAPH_API}/createPage",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        if resp.get("ok") and resp.get("result", {}).get("url"):
            url = resp["result"]["url"]
            state.update({
                "last_sent_date": day,
                "last_sent_at_utc": dt.datetime.now(dt.UTC).isoformat(),
                "last_url": url,
            })
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps(state, indent=2))
            print(f"🌐 {url}")
            return 0
        print(f"[telegraph] API error: {resp}", file=sys.stderr)
    except Exception as e:
        print(f"[telegraph] publish: {e}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
