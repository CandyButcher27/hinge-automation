import pytest
from PIL import Image, ImageDraw

import hinge

PHOTOS = [400, 1300, 2300]
PROMPT = 900


def page():
    im = Image.effect_noise((hinge.FW, 3000), 60).convert("RGB")
    ImageDraw.Draw(im).rectangle((20, PROMPT - 200, 395, PROMPT + 40), fill="white")
    w, h = hinge.HEART.size
    for y in PHOTOS + [PROMPT]:
        ImageDraw.Draw(im).ellipse((336, y - 24, 384, y + 24), fill="black")
        im.paste(hinge.HEART.convert("RGB"), (346, y - h // 2))
    return im


def frames(tops):
    im = page()
    return [im.crop((0, t, hinge.FW, t + hinge.FH)) for t in tops]


def test_offset_forward_and_back():
    a, b = frames([500, 800])
    assert hinge.offset(a, b) == 300
    assert hinge.offset(b, a) == -300


def test_map_profile_finds_photos_not_prompt():
    tops = [0, 350, 700, 600, 950, 1300, 1650, 2000]
    top, photos = hinge.map_profile([(f, f, set()) for f in frames(tops)])
    assert top == tops[-1]
    assert len(photos) == len(PHOTOS)
    assert all(abs(p - e) <= 2 for p, e in zip(photos, PHOTOS))


def test_still_masks_video_and_keeps_offset():
    a, b = frames([500, 800])
    a2, b2 = a.copy(), b.copy()
    for im, y in ((a2, 700), (b2, 400)):
        im.paste(Image.effect_noise((375, 150), 90).convert("RGB"), (20, y))
    _, flat_a, moving = hinge.still(a, a2)
    assert set(range(700, 850)) <= moving
    _, flat_b, _ = hinge.still(b, b2)
    assert hinge.offset(flat_a, flat_b) == 300


def test_offset_ignores_video_that_starts_playing():
    a, b = frames([500, 800])
    ImageDraw.Draw(a).rectangle((20, 700, 395, 1000), fill="black")
    b2 = b.copy()
    b2.paste(Image.effect_noise((375, 300), 90).convert("RGB"), (20, 400))
    _, flat_b, moving = hinge.still(b, b2)
    assert set(range(400, 700)) <= moving
    assert hinge.offset(a, flat_b) == 300


def test_unmoved_treats_unmatchable_frames_as_moved():
    a, b = frames([0, 0])
    assert hinge.unmoved(a, b)
    assert not hinge.unmoved(a, Image.effect_noise((hinge.FW, hinge.FH), 90).convert("RGB"))


def test_look_waits_for_scrolling_to_settle(monkeypatch):
    a, b = frames([500, 800])
    shots = iter([a, b, a, a])
    monkeypatch.setattr(hinge, "screen", lambda: next(shots))
    monkeypatch.setattr(hinge, "frame", lambda im: im)
    monkeypatch.setattr(hinge.time, "sleep", lambda s: None)
    _, _, _, moving = hinge.look()
    assert not moving
    assert next(shots, None) is None


def test_skip_waits_for_a_new_profile(monkeypatch):
    old, new = frames([0, 1300])
    shots = iter([old, old, new])
    monkeypatch.setattr(hinge, "screen", lambda: next(shots))
    monkeypatch.setattr(hinge, "frame", lambda im: im)
    monkeypatch.setattr(hinge, "tap", lambda x, y: None)
    monkeypatch.setattr(hinge, "profile_screen", lambda im: True)
    monkeypatch.setattr(hinge.time, "sleep", lambda s: None)
    hinge.skip()
    assert next(shots, None) is None


def test_find_send_scrolls_until_the_pill_shows(monkeypatch):
    found = iter([None, None, 700])
    strokes = []
    monkeypatch.setattr(hinge, "screen", lambda: None)
    monkeypatch.setattr(hinge, "frame", lambda im: im)
    monkeypatch.setattr(hinge, "send_button", lambda im: next(found))
    monkeypatch.setattr(hinge, "stroke", strokes.append)
    monkeypatch.setattr(hinge, "pause", lambda *a: None)
    assert hinge.find_send() == 700
    assert len(strokes) == 2


@pytest.fixture
def app(tmp_path, monkeypatch):
    sent = []
    monkeypatch.setattr(hinge, "PEOPLE", tmp_path / "people")
    monkeypatch.setattr(hinge, "LOG", tmp_path / "people" / "likes.log")
    hinge.PEOPLE.mkdir()
    for name in ("rewind", "skip", "pause"):
        monkeypatch.setattr(hinge, name, lambda *a: None)
    monkeypatch.setattr(hinge, "wander", lambda folder: folder.mkdir(exist_ok=True) or [400])
    monkeypatch.setattr(hinge, "open_sheet", lambda hy, comment: sent.append(comment) or 700)
    monkeypatch.setattr(hinge, "send_like", lambda py: False)
    return sent


def test_auto_likes_without_asking_until_the_cap(app):
    def ask(q):
        raise AssertionError("auto mode asked")
    hinge.run(2, "list", False, auto=True, ask=ask, say=lambda m: None)
    assert len(app) == 2
    assert hinge.liked_today() == 2


def test_run_stops_when_asked_to(app):
    hinge.run(5, "list", False, auto=True, say=lambda m: None, stopped=lambda: len(app) >= 1)
    assert len(app) == 1


def test_restrictive_mode_lets_the_person_replace_the_comment(app):
    answers = iter(["y", "nice sunset, where is this?", "y", "café?", "-", "q"])
    hinge.run(5, "list", False, ask=lambda q: next(answers), say=lambda m: None)
    assert app == ["nice sunset, where is this?", None]


def test_ascii_text_keeps_what_the_console_can_type():
    assert hinge.ascii_text("it’s “lovely” — wow… \U0001F60D ok") == 'it\'s "lovely" - wow... ok'


def test_model_comment_is_used_and_falls_back_to_the_list(app, monkeypatch):
    monkeypatch.setattr(hinge, "screen", lambda: None)
    monkeypatch.setattr(hinge, "frame", lambda im: Image.new("RGB", (hinge.FW, hinge.FH)))
    monkeypatch.setattr(hinge, "resolve_provider", lambda p: "claude-cli")
    replies = iter(["love the lighting in this one \U0001F31E", RuntimeError("offline")])

    def photo_comment(png, provider):
        r = next(replies)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(hinge, "photo_comment", photo_comment)
    hinge.run(2, "model", False, auto=True, say=lambda m: None)
    lines = [line.strip() for line in hinge.COMMENTS.read_text().splitlines() if line.strip()]
    assert app[0] == "love the lighting in this one"
    assert app[1] in lines


def test_auto_mode_does_not_like_after_stop_during_the_scan(app, monkeypatch):
    flag = []
    monkeypatch.setattr(hinge, "wander", lambda folder: folder.mkdir(exist_ok=True) or flag.append(1) or [400])
    hinge.run(5, "list", False, auto=True, say=lambda m: None, stopped=lambda: bool(flag))
    assert app == []
