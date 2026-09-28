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
