from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL = os.environ.get("HINGE_ANTHROPIC_MODEL", "claude-opus-5")
OPENAI_MODEL = os.environ.get("HINGE_OPENAI_MODEL", "gpt-5.4-mini")
CLAUDE_CLI_MODEL = os.environ.get("HINGE_CLAUDE_CLI_MODEL", "haiku")
DB_PATH = Path(__file__).resolve().parent.parent / "dating-assistant" / "data" / "assistant.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY, category TEXT NOT NULL, value TEXT NOT NULL,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS idx_preferences_category ON preferences(category);
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY, name TEXT, age INTEGER, occupation TEXT, location TEXT,
    bio TEXT, notes TEXT, user_rating INTEGER, fingerprint TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_fingerprint ON profiles(fingerprint);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL, content TEXT NOT NULL,
    created_at TEXT NOT NULL, FOREIGN KEY(profile_id) REFERENCES profiles(id));
CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY, profile_id INTEGER, draft TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL,
    FOREIGN KEY(profile_id) REFERENCES profiles(id));
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "is_profile": {
            "type": "boolean",
            "description": "True only if the screenshot shows a dating profile. False for anything else.",
        },
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "occupation": {"type": "string"},
        "location": {"type": "string"},
        "prompts": {
            "type": "array",
            "description": "Every visible written prompt, as 'Prompt title -> their answer'.",
            "items": {"type": "string"},
        },
        "photos": {
            "type": "array",
            "description": "One short factual description per visible photo, in screen order.",
            "items": {"type": "string"},
        },
        "target_type": {"type": "string", "enum": ["photo", "prompt"]},
        "target": {
            "type": "string",
            "description": "Which photo or prompt the comment attaches to, quoted or described so the user can find it on screen.",
        },
        "why_this_target": {"type": "string"},
        "comment": {
            "type": "string",
            "description": "The message to send. Under 200 characters unless the hook needs more.",
        },
        "alternate": {"type": "string", "description": "A second, different-angle option."},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "is_profile",
        "name",
        "age",
        "occupation",
        "location",
        "prompts",
        "photos",
        "target_type",
        "target",
        "why_this_target",
        "comment",
        "alternate",
        "uncertainties",
    ],
    "additionalProperties": False,
}

SYSTEM = """You read a screenshot of a dating profile that the user is looking at on their own screen, and you write the opening comment they will send.

Transcribe only what is visible. If a field is not on screen, use an empty string for text fields, 0 for age, and add a line to `uncertainties` - never invent a detail.

If the screenshot is not a dating profile, set is_profile to false, leave the other fields empty, and stop.

Writing the comment:
- Attach it to the single strongest hook on screen - a specific prompt answer or a specific detail in a photo. Name that target so the user knows where to tap.
- Be specific to this person. A comment that would work on any profile is a failure.
- No pickup lines, no compliments about their body, no questions they have answered on the profile already.
- Sound like a person typing on their phone: lowercase is fine, one thought, usually one or two sentences.
- End on something they can easily answer.
- Respect the user's saved preferences below. Deal breakers are hard constraints - if the profile visibly conflicts with one, still write the comment but say so in `uncertainties`.
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(profiles)")}
    if cols and "fingerprint" not in cols:
        conn.execute("ALTER TABLE profiles ADD COLUMN fingerprint TEXT")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def fingerprint(data: dict) -> str:
    parts = [
        str(data.get("name", "")).strip().lower(),
        str(data.get("age", "")),
        str(data.get("occupation", "")).strip().lower(),
        *sorted(p.strip().lower() for p in data.get("prompts", [])),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def load_preferences(conn: sqlite3.Connection) -> str:
    rows = conn.execute("SELECT category, value FROM preferences ORDER BY category").fetchall()
    if not rows:
        return "The user has not saved any preferences yet."
    return "\n".join(f"- {r['category']}: {r['value']}" for r in rows)


def window_region(title: str) -> tuple[int, int, int, int]:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    matches: list[tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if not length:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if title.lower() in buf.value.lower():
            matches.append((hwnd, buf.value))
        return True

    user32.EnumWindows(visit, 0)
    if not matches:
        raise RuntimeError(f"no visible window matching {title!r} - is scrcpy running?")
    hwnd, found = matches[0]
    rect = wintypes.RECT()
    origin = wintypes.POINT(0, 0)
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    user32.ClientToScreen(hwnd, ctypes.byref(origin))
    if rect.right < 50 or rect.bottom < 50:
        raise RuntimeError(f"window {found!r} is {rect.right}x{rect.bottom} - minimized?")
    return (origin.x, origin.y, rect.right, rect.bottom)


def list_windows() -> None:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(hwnd, _):
        length = user32.GetWindowTextLengthW(hwnd)
        if user32.IsWindowVisible(hwnd) and length:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            print(f"  {buf.value}")
        return True

    print("visible windows:")
    user32.EnumWindows(visit, 0)


def grab(region: tuple[int, int, int, int] | None, monitor: int) -> bytes:
    import mss
    import mss.tools

    with mss.mss() as sct:
        if region:
            x, y, w, h = region
            box = {"left": x, "top": y, "width": w, "height": h}
        else:
            box = sct.monitors[monitor]
        shot = sct.grab(box)
        return mss.tools.to_png(shot.rgb, shot.size)


def shrink(png: bytes, max_edge: int = 1568) -> bytes:
    try:
        from PIL import Image
    except ImportError:
        return png
    img = Image.open(io.BytesIO(png))
    if max(img.size) <= max_edge:
        return png
    scale = max_edge / max(img.size)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


PROMPT = "Read this profile and write my opening comment."


def resolve_provider(choice: str) -> str:
    if choice != "auto":
        return choice
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if shutil.which("claude"):
        return "claude-cli"
    raise RuntimeError("set ANTHROPIC_API_KEY or OPENAI_API_KEY, or install the claude CLI")


def analyze(png: bytes, preferences: str, provider: str = "anthropic") -> dict:
    system = f"{SYSTEM}\n\nThe user's saved preferences:\n{preferences}"
    if provider == "openai":
        return analyze_openai(png, system)
    if provider == "claude-cli":
        return analyze_claude_cli(png, system)
    return analyze_anthropic(png, system)


def unfence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return text.strip()


def analyze_claude_cli(png: bytes, system: str) -> dict:
    shot = Path(tempfile.gettempdir()) / f"hinge_shot_{os.getpid()}.png"
    shot.write_bytes(png)
    prompt = (
        f"{system}\n\nRead the image at {shot} and reply with ONLY a JSON object matching this "
        f"schema. No prose, no code fences.\n\n{json.dumps(RESPONSE_SCHEMA)}"
    )
    try:
        run = subprocess.run(
            [
                "claude", "-p", prompt,
                "--output-format", "json",
                "--allowedTools", "Read",
                "--strict-mcp-config",
                "--model", CLAUDE_CLI_MODEL,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    finally:
        shot.unlink(missing_ok=True)
    if run.returncode != 0:
        raise RuntimeError(f"claude cli exited {run.returncode}: {run.stderr.strip()[:400]}")
    payload = json.loads(run.stdout)
    if payload.get("is_error"):
        raise RuntimeError(f"claude cli failed: {payload.get('result')}")
    return json.loads(unfence(payload["result"]))


def analyze_anthropic(png: bytes, system: str) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=system,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.standard_b64encode(png).decode(),
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": RESPONSE_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"model declined: {response.stop_details}")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def analyze_openai(png: bytes, system: str) -> dict:
    import openai

    client = openai.OpenAI()
    response = client.responses.create(
        model=OPENAI_MODEL,
        max_output_tokens=16000,
        instructions=system,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "detail": "high",
                        "image_url": "data:image/png;base64,"
                        + base64.standard_b64encode(png).decode(),
                    },
                    {"type": "input_text", "text": PROMPT},
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "profile_comment",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            }
        },
    )
    refusal = next(
        (
            block.refusal
            for item in response.output
            for block in getattr(item, "content", None) or []
            if block.type == "refusal"
        ),
        None,
    )
    if refusal:
        raise RuntimeError(f"model declined: {refusal}")
    if response.status == "incomplete":
        raise RuntimeError(f"response cut short: {response.incomplete_details}")
    return json.loads(response.output_text)


def persist(conn: sqlite3.Connection, data: dict) -> tuple[int, bool]:
    fp = fingerprint(data)
    row = conn.execute("SELECT id FROM profiles WHERE fingerprint = ?", (fp,)).fetchone()
    bio = "\n".join(data.get("prompts", []))
    notes = "photos: " + " | ".join(data.get("photos", []))
    ts = now()
    if row:
        conn.execute(
            "UPDATE profiles SET bio = ?, notes = ?, updated_at = ? WHERE id = ?",
            (bio, notes, ts, row["id"]),
        )
        profile_id, seen_before = row["id"], True
    else:
        cur = conn.execute(
            """INSERT INTO profiles (name, age, occupation, location, bio, notes, fingerprint,
                                     created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("name") or None,
                data.get("age") or None,
                data.get("occupation") or None,
                data.get("location") or None,
                bio,
                notes,
                fp,
                ts,
                ts,
            ),
        )
        profile_id, seen_before = cur.lastrowid, False
    conn.execute(
        "INSERT INTO drafts (profile_id, draft, status, created_at) VALUES (?, ?, 'draft', ?)",
        (profile_id, data["comment"], ts),
    )
    conn.commit()
    return profile_id, seen_before


def to_clipboard(text: str) -> None:
    import ctypes
    from ctypes import wintypes

    u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
    k32.GlobalAlloc.restype = wintypes.HGLOBAL
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    k32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    u32.SetClipboardData.restype = wintypes.HANDLE
    u32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]

    data = text.encode("utf-16-le") + b"\x00\x00"
    handle = k32.GlobalAlloc(0x2000, len(data))
    ctypes.memmove(k32.GlobalLock(handle), data, len(data))
    k32.GlobalUnlock(handle)
    if not u32.OpenClipboard(None):
        raise RuntimeError("could not open the clipboard - another app is holding it")
    try:
        u32.EmptyClipboard()
        u32.SetClipboardData(13, handle)
    finally:
        u32.CloseClipboard()


def report(data: dict, profile_id: int, seen_before: bool) -> None:
    who = data.get("name") or "unnamed"
    age = data.get("age") or "?"
    print(f"\n--- profile #{profile_id}: {who}, {age}" + ("  [seen before]" if seen_before else ""))
    print(f"target ({data['target_type']}): {data['target']}")
    print(f"why: {data['why_this_target']}")
    print(f"\n  >> {data['comment']}\n")
    print(f"alt: {data['alternate']}")
    for u in data.get("uncertainties", []):
        print(f"  ? {u}")
    print("copied to clipboard - paste it into the app yourself")


def run_once(
    conn: sqlite3.Connection,
    region,
    monitor: int,
    image: str | None = None,
    window: str | None = None,
    provider: str = "anthropic",
) -> None:
    if image:
        png = shrink(Path(image).read_bytes())
    else:
        png = shrink(grab(window_region(window) if window else region, monitor))
    data = analyze(png, load_preferences(conn), provider)
    if not data.get("is_profile"):
        print("no profile on screen - nothing drafted")
        return
    profile_id, seen_before = persist(conn, data)
    to_clipboard(data["comment"])
    report(data, profile_id, seen_before)


def parse_region(value: str | None):
    if not value:
        return None
    parts = [int(p) for p in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("region must be x,y,width,height")
    return tuple(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Screenshot -> profile analysis -> comment on clipboard.")
    ap.add_argument("--once", action="store_true", help="capture immediately and exit")
    ap.add_argument("--image", help="analyze this PNG instead of grabbing the screen (implies --once)")
    ap.add_argument("--region", type=parse_region, default=os.environ.get("HINGE_REGION"))
    ap.add_argument(
        "--window",
        default=os.environ.get("HINGE_WINDOW"),
        help="grab this window by title substring, tracked as it moves (e.g. scrcpy)",
    )
    ap.add_argument("--list-windows", action="store_true", help="print visible window titles and exit")
    ap.add_argument("--monitor", type=int, default=1, help="mss monitor index (0 = all)")
    ap.add_argument("--hotkey", default="<ctrl>+<alt>+h")
    ap.add_argument("--delay", type=float, default=0.4, help="seconds to wait before grabbing")
    ap.add_argument(
        "--provider",
        choices=["auto", "anthropic", "openai", "claude-cli"],
        default=os.environ.get("HINGE_PROVIDER", "auto"),
        help="which vision model writes the comment (auto: API key if set, else the claude CLI)",
    )
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.list_windows:
        list_windows()
        return 0
    region = args.region if isinstance(args.region, tuple) else parse_region(args.region)
    provider = resolve_provider(args.provider)

    conn = connect()

    if args.once or args.image:
        if not args.image:
            time.sleep(args.delay)
        run_once(conn, region, args.monitor, args.image, args.window, provider)
        return 0

    from pynput import keyboard

    source = f"window {args.window!r}" if args.window else (f"region {region}" if region else f"monitor {args.monitor}")
    model = {"anthropic": MODEL, "openai": OPENAI_MODEL, "claude-cli": CLAUDE_CLI_MODEL}[provider]
    print(f"listening on {args.hotkey} - capturing {source} - ctrl+c here to quit")
    print(f"model: {model}")
    print(f"db: {DB_PATH}")

    def fire():
        try:
            time.sleep(args.delay)
            run_once(conn, region, args.monitor, None, args.window, provider)
        except Exception as exc:
            print(f"failed: {exc}", file=sys.stderr)

    with keyboard.GlobalHotKeys({args.hotkey: fire}) as listener:
        listener.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
