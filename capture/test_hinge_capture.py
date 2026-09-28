import os
import sqlite3

import pytest

import hinge_capture as hc


@pytest.fixture
def conn(tmp_path):
    return hc.connect(tmp_path / "test.db")


PROFILE = {
    "is_profile": True,
    "name": "Sam",
    "age": 24,
    "occupation": "Software engineer",
    "location": "Bangalore",
    "prompts": ["My simple pleasures -> finding a new coffee shop and staying three hours"],
    "photos": ["standing on a ridge with a backpack"],
    "target_type": "prompt",
    "target": "My simple pleasures",
    "why_this_target": "most specific detail on screen",
    "comment": "three hours is a commitment. what are you ordering?",
    "alternate": "which shop is winning right now?",
    "uncertainties": [],
}


def test_fingerprint_is_stable_and_order_independent():
    a = hc.fingerprint(PROFILE)
    reordered = {**PROFILE, "prompts": list(reversed(PROFILE["prompts"] + ["Fact -> b"]))}
    forward = {**PROFILE, "prompts": PROFILE["prompts"] + ["Fact -> b"]}
    assert a == hc.fingerprint(dict(PROFILE))
    assert hc.fingerprint(reordered) == hc.fingerprint(forward)
    assert len(a) == 64


def test_fingerprint_changes_with_person():
    assert hc.fingerprint(PROFILE) != hc.fingerprint({**PROFILE, "name": "Alex"})
    assert hc.fingerprint(PROFILE) != hc.fingerprint({**PROFILE, "age": 25})


def test_persist_creates_then_dedupes(conn):
    profile_id, seen = hc.persist(conn, PROFILE)
    assert seen is False
    again_id, seen_again = hc.persist(conn, PROFILE)
    assert (again_id, seen_again) == (profile_id, True)
    assert conn.execute("SELECT count(*) FROM profiles").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM drafts").fetchone()[0] == 2

    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    assert row["name"] == "Sam"
    assert row["age"] == 24
    assert "coffee shop" in row["bio"]
    assert "ridge" in row["notes"]


def test_empty_fields_stored_as_null(conn):
    sparse = {**PROFILE, "name": "", "age": 0, "occupation": "", "location": ""}
    profile_id, _ = hc.persist(conn, sparse)
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    assert row["name"] is None
    assert row["age"] is None


def test_preferences_render(conn):
    assert "not saved any preferences" in hc.load_preferences(conn)
    ts = hc.now()
    conn.execute(
        "INSERT INTO preferences (category, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("deal breakers", "smoking", ts, ts),
    )
    conn.commit()
    assert "- deal breakers: smoking" in hc.load_preferences(conn)


def test_connect_migrates_an_old_db(tmp_path):
    path = tmp_path / "old.db"
    old = sqlite3.connect(path)
    old.execute(
        """CREATE TABLE profiles (id INTEGER PRIMARY KEY, name TEXT, age INTEGER,
           occupation TEXT, location TEXT, bio TEXT, notes TEXT, user_rating INTEGER,
           created_at TEXT NOT NULL, updated_at TEXT NOT NULL)"""
    )
    old.execute(
        "INSERT INTO profiles (name, created_at, updated_at) VALUES ('Old', 'x', 'x')"
    )
    old.commit()
    old.close()

    migrated = hc.connect(path)
    cols = {r["name"] for r in migrated.execute("PRAGMA table_info(profiles)")}
    assert "fingerprint" in cols
    assert migrated.execute("SELECT count(*) FROM profiles").fetchone()[0] == 1
    hc.persist(migrated, PROFILE)
    assert migrated.execute("SELECT count(*) FROM profiles").fetchone()[0] == 2


def test_parse_region():
    assert hc.parse_region("0,0,1080,1920") == (0, 0, 1080, 1920)
    assert hc.parse_region(None) is None
    with pytest.raises(Exception):
        hc.parse_region("1,2,3")


def test_response_schema_is_strict():
    schema = hc.RESPONSE_SCHEMA
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])


def test_connection_usable_from_the_hotkey_thread(conn):
    import threading

    box = {}

    def work():
        try:
            hc.persist(conn, PROFILE)
        except Exception as exc:
            box["err"] = exc

    t = threading.Thread(target=work)
    t.start()
    t.join()
    assert "err" not in box, box.get("err")
    assert conn.execute("SELECT count(*) FROM profiles").fetchone()[0] == 1


def test_unfence_strips_code_fences():
    assert hc.unfence('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert hc.unfence('```\n{"a": 1}\n```') == '{"a": 1}'
    assert hc.unfence('  {"a": 1}  ') == '{"a": 1}'


def test_resolve_provider(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(hc.shutil, "which", lambda _: None)

    assert hc.resolve_provider("openai") == "openai"
    with pytest.raises(RuntimeError):
        hc.resolve_provider("auto")

    monkeypatch.setattr(hc.shutil, "which", lambda _: r"C:\claude.exe")
    assert hc.resolve_provider("auto") == "claude-cli"

    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    assert hc.resolve_provider("auto") == "openai"

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    assert hc.resolve_provider("auto") == "anthropic"



def test_load_env_fills_only_unset_variables(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# HINGE_AVD=commented\nHINGE_OPENAI_MODEL="from-file"\nHINGE_PROVIDER=openai\n', encoding="utf-8")
    monkeypatch.setenv("HINGE_PROVIDER", "shell")
    monkeypatch.delenv("HINGE_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("HINGE_AVD", raising=False)
    hc.load_env(env)
    assert os.environ["HINGE_OPENAI_MODEL"] == "from-file"
    assert os.environ["HINGE_PROVIDER"] == "shell"
    assert "HINGE_AVD" not in os.environ
    hc.load_env(tmp_path / "missing.env")
