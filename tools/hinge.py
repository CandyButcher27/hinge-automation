import argparse
import ctypes
import functools
import io
import math
import os
import random
import re
import shutil
import socket
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "capture"))
from hinge_capture import grab, window_region

AVD = os.environ.get("HINGE_AVD", "Medium_Phone_API_35")
PORT = int(os.environ.get("HINGE_CONSOLE_PORT", "5554"))
WINDOW = f"Android Emulator - {AVD}"
FW, FH = 415, 923
SX, SY = 1080 / FW, 2400 / FH
TOP, BOTTOM = 70, 836
SKIP = (134, 2043)
HEART = Image.open(Path(__file__).with_name("heart.png")).convert("L")
COMMENTS = Path(__file__).resolve().parents[1] / "prompts.txt"
PEOPLE = Path(__file__).resolve().parents[1] / "people"
LOG = PEOPLE / "likes.log"
LAST = Path(tempfile.gettempdir(), "hinge_last.png")


class Stop(Exception):
    pass


def pause(lo=0.8, hi=2.2):
    time.sleep(random.uniform(lo, hi))


@functools.cache
def console():
    c = socket.create_connection(("127.0.0.1", PORT))
    c.sendall(f"auth {(Path.home() / '.emulator_console_auth_token').read_text().strip()}\n".encode())
    return c


def send(*evs):
    console().sendall(("event send " + " ".join(evs) + " EV_SYN:0:0\n").encode())


def check():
    time.sleep(0.05)
    if b"KO" in console().recv(65536):
        raise RuntimeError("emulator console rejected an event")


def type_text(text):
    if not (text.isascii() and text.isprintable()):
        raise ValueError(f"cannot type {text!r}: printable ASCII only")
    for chunk in re.findall(r"\S ?", " ".join(text.split())):
        console().sendall(f"event text {chunk}\n".encode())
        time.sleep(random.uniform(0.35, 0.9) if chunk.endswith(" ") else random.lognormvariate(math.log(0.14), 0.35))
    time.sleep(0.3)
    check()


def touch(pts, dt):
    def at(x, y, p):
        return f"EV_ABS:ABS_MT_POSITION_X:{round(x * 32767 / 1080)}", f"EV_ABS:ABS_MT_POSITION_Y:{round(y * 32767 / 2400)}", f"EV_ABS:ABS_MT_PRESSURE:{round(p)}"

    major = random.randint(1200, 2200)
    send("EV_ABS:ABS_MT_SLOT:0", f"EV_ABS:ABS_MT_TRACKING_ID:{random.randint(1, 65000)}",
         f"EV_ABS:ABS_MT_TOUCH_MAJOR:{major}", f"EV_ABS:ABS_MT_TOUCH_MINOR:{round(major * random.uniform(0.75, 0.95))}", *at(*pts[0]))
    for pt in pts[1:]:
        time.sleep(dt * random.uniform(0.8, 1.2))
        send(*at(*pt))
    time.sleep(dt)
    send("EV_ABS:ABS_MT_TRACKING_ID:-1")
    check()


def tap(x, y):
    x, y = x + random.triangular(-12, 12), y + random.triangular(-12, 12)
    p = random.randint(150, 500)
    touch([(x + random.uniform(-2, 2), y + random.uniform(-2, 2), p + random.uniform(-40, 40)) for _ in range(random.randint(3, 7))],
          random.uniform(0.012, 0.025))
    pause()


def drag(x1, y1, x2, y2, dur):
    n = max(6, dur // 16)
    bow = random.uniform(-30, 30)
    p = random.randint(150, 500)
    pts = [(x1 + random.uniform(-1, 1), y1 + random.uniform(-1, 1), p * 0.75 + random.uniform(-15, 15)) for _ in range(random.randint(0, 8))]
    for i in range(n + 1):
        t = i / n
        s = t**3 * (10 - 15 * t + 6 * t * t)
        pts.append((x1 + (x2 - x1) * s + bow * math.sin(math.pi * s), y1 + (y2 - y1) * s,
                    p * (0.75 + 0.25 * math.sin(math.pi * t)) + random.uniform(-15, 15)))
    touch(pts, dur / n / 1000)


def thumb(down=False):
    x = random.randint(90, 260) if random.random() < 0.5 else random.randint(820, 1000)
    return x, random.randint(500, 900) if down else random.randint(1650, 1880)


def stroke(dist):
    x, y = thumb(dist < 0)
    drag(x, y, x + random.randint(-60, 60), y - dist, int(abs(dist) / random.uniform(0.6, 1.8)))


def flick(back_ok):
    dist = random.randint(450, 1000)
    if back_ok and random.random() < 0.1:
        dist = -random.randint(150, 350)
    stroke(dist)
    pause(2.5, 5.0) if random.random() < 0.25 else pause(0.9, 2.2)
    return dist > 0


def screen():
    hwnd = ctypes.windll.user32.FindWindowW(None, f"{WINDOW}:{PORT}")
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x13)
    return grab(window_region(WINDOW), 1)


def frame(png):
    return Image.open(io.BytesIO(png)).convert("RGB").resize((FW, FH))


def still(a, b):
    rows = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 24 else 0).resize((1, FH), Image.BOX).tobytes()
    moving = {r for y, v in enumerate(rows) if v > 3 for r in range(y - 4, y + 5)}
    flat = a.copy()
    draw = ImageDraw.Draw(flat)
    for y in moving:
        draw.line((0, y, FW, y), fill=(128, 128, 128))
    return a, flat, moving


def look():
    for _ in range(6):
        png = screen()
        time.sleep(0.4)
        view = still(frame(png), frame(screen()))
        if sum(TOP <= y < BOTTOM for y in view[2]) < 0.6 * (BOTTOM - TOP):
            break
    return png, *view


def shot(path=LAST):
    path.write_bytes(screen())
    print(path)


def diff(a, b):
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def blank(g, y):
    st = ImageStat.Stat(g.crop((250, y - 40, 320, y - 12)))
    return st.mean[0] > 235 and st.stddev[0] < 10


def hearts(im):
    g = im.convert("L")
    w, h = HEART.size
    rows = [y for y in range(TOP, BOTTOM - h) if g.getpixel((342, y + h // 2)) < 60]
    scores = sorted((diff(HEART, g.crop((x, y, x + w, y + h))), y + h // 2) for x in range(345, 348) for y in rows)
    found = []
    for d, y in scores:
        if d > 30:
            break
        if all(abs(y - f) > 40 for f in found):
            found.append(y)
    return sorted((y, not blank(g, y)) for y in found)


def offset(a, b):
    a, b = (im.convert("L").crop((100, 0, 395, FH)) for im in (a, b))
    small = [im.resize((im.width // 4, im.height // 4)) for im in (a, b)]
    grey = [[v == 0 for v in im.point(lambda v: 0 if v == 128 else 255).resize((1, FH), Image.BOX).tobytes()] for im in (a, b)]
    grey_small = [[any(g[4 * r:4 * r + 4]) for r in range(FH // 4)] for g in grey]

    def score(pa, pb, ga, gb, d, k):
        y0, y1 = max(TOP, TOP - d) // k, min(BOTTOM, BOTTOM - d) // k
        if y1 - y0 < 200 // k:
            return math.inf
        rows = ImageChops.difference(pb.crop((0, y0, pb.width, y1)), pa.crop((0, y0 + d // k, pa.width, y1 + d // k)))
        keep = [v for i, v in enumerate(rows.resize((1, y1 - y0), Image.BOX).tobytes()) if not (gb[y0 + i] or ga[y0 + i + d // k])]
        if len(keep) < 200 // k:
            return math.inf
        return sum(keep) / len(keep)

    _, d = min((score(*small, *grey_small, d, 4), d) for d in range(-400, 452, 4))
    s, d = min((score(a, b, *grey, e, 1), e) for e in range(d - 4, d + 5))
    if s > 15:
        raise Stop(f"lost track of the scroll position (diff {s:.1f})")
    return d


def unmoved(a, b):
    try:
        return abs(offset(a, b)) <= 2
    except Stop:
        return False


def kinds(view):
    im, _, moving = view
    return [(y, photo and not any(r in moving for r in range(y - 120, y - 40))) for y, photo in hearts(im)]


def visible(view):
    return [y for y, ok in kinds(view) if ok and 150 <= y <= 780]


def map_profile(views):
    ys = [0]
    for a, b in zip(views, views[1:]):
        ys.append(ys[-1] + offset(a[1], b[1]))
    seen = []
    for top, view in zip(ys, views):
        for y, ok in kinds(view):
            if all(abs(top + y - s) > 25 for s, _ in seen):
                seen.append((top + y, ok))
    return ys[-1], sorted(cy for cy, ok in seen if ok)


def goto(cy, top, view):
    for _ in range(20):
        want = cy - top
        if 150 <= want <= 780:
            near = [y for y in visible(view) if abs(y - want) < 40]
            if near:
                return near[0]
        stroke(max(-300, min(300, want - 450)) * SY)
        pause(0.9, 1.8)
        new = look()[1:]
        top += offset(view[1], new[1])
        view = new
    raise Stop("could not scroll to the chosen photo")


def purple(px):
    r, g, b = px
    return b > g + 15 and r > g and 130 < (r + g + b) / 3 < 235


def whiteish(g, y):
    return sum(g.crop((160, y, 370, y + 1)).histogram()[236:]) > 0.8 * 210


def darkish(g, y):
    return sum(g.crop((160, y, 370, y + 1)).histogram()[:60]) > 0.6 * 210


def send_button(im):
    g = im.convert("L")
    for y in range(TOP + 30, BOTTOM - 50):
        if darkish(g, y) and darkish(g, y + 30) and whiteish(g, y - 26) and whiteish(g, y + 50) and purple(im.getpixel((85, y + 20))):
            return y + 20
    return None


def rose_sheet(im):
    g = im.convert("L")
    if ImageStat.Stat(g.crop((100, 35, 300, 60))).mean[0] > 200:
        return None
    if sum(purple(im.getpixel((x, y))) for x in range(180, 236, 4) for y in range(530, 590, 4)) < 20:
        return None
    for y in range(680, 840):
        if g.getpixel((150, y)) < 60 and g.getpixel((265, y)) < 60 and g.getpixel((207, y - 20)) > 200:
            return y + 24
    return None


def profile_screen(im):
    return ImageStat.Stat(im.convert("L").crop((100, 35, 300, 60))).mean[0] > 200 and send_button(im) is None and any(p for _, p in hearts(im))


def scroll(folder):
    folder.mkdir(parents=True, exist_ok=True)
    views, forward = [], False
    for i in range(1, 41):
        png, *view = look()
        if forward and unmoved(views[-1][1], view[1]):
            break
        (folder / f"{i:02}.png").write_bytes(png)
        views.append(view)
        forward = flick(i > 1)
    return views


def wander(folder):
    folder.mkdir(parents=True, exist_ok=True)
    depth = random.randint(0, 8)
    views, forward = [], False
    for i in range(1, 41):
        png, *view = look()
        end = forward and unmoved(views[-1][1], view[1])
        if not end:
            (folder / f"{i:02}.png").write_bytes(png)
            views.append(view)
        if visible(view) and (i > depth or end):
            return visible(view)
        if end:
            break
        forward = flick(i > 1)
    for _ in range(10):
        stroke(-random.randint(400, 600))
        pause(0.9, 1.8)
        ys = visible(look()[1:])
        if ys:
            return ys
    raise Stop("no photo found on this profile")


def rewind():
    prev = look()[2]
    for _ in range(15):
        stroke(-random.randint(600, 750))
        pause(0.6, 1.4)
        cur = look()[2]
        if unmoved(prev, cur):
            return
        prev = cur


def find_send():
    for _ in range(3):
        py = send_button(frame(screen()))
        if py is not None:
            return py
        stroke(random.randint(300, 500))
        pause(1.0, 2.0)
    return None


def open_sheet(hy, comment):
    tap(360 * SX, hy * SY)
    stroke(random.randint(500, 700))
    pause(1.2, 2.6)
    py = find_send()
    if py is None:
        raise Stop("like sheet not found after tapping the heart")
    if comment:
        tap(207 * SX, (py - 68) * SY)
        type_text(comment)
        pause()
        py = find_send()
        if py is None:
            raise Stop("Send button not found after typing")
    return py


def send_like(py):
    tap(263 * SX, py * SY)
    rose, start = False, time.time()
    while time.time() - start < 20:
        time.sleep(1.5)
        im = frame(screen())
        ry = rose_sheet(im)
        if ry and not rose:
            tap(207 * SX, (ry + 60) * SY)
            rose = True
        elif profile_screen(im):
            return rose
    im.save(LAST)
    raise Stop(f"unexpected screen after Send, see {LAST}")


def skip():
    before = frame(screen())
    tap(*SKIP)
    start = time.time()
    while time.time() - start < 10:
        time.sleep(1)
        im = frame(screen())
        if diff(before, im) > 25 and profile_screen(im):
            return
    im.save(LAST)
    raise Stop(f"Skip did not bring up the next profile, see {LAST}")


def liked_today():
    today = time.strftime("%Y-%m-%d")
    return sum(line.startswith(today) for line in LOG.read_text().splitlines()) if LOG.exists() else 0


def run(cap, no_comment, full):
    comments = [None] if no_comment else [line.strip() for line in COMMENTS.read_text().splitlines() if line.strip()]
    for c in comments:
        if c and not (c.isascii() and c.isprintable()):
            raise Stop(f"comment {c!r} is not printable ASCII")
    while True:
        if liked_today() >= cap:
            print(f"daily cap of {cap} likes reached")
            return
        tmp = Path(tempfile.mkdtemp())
        print("scanning profile...", flush=True)
        rewind()
        if full:
            views = scroll(tmp)
            top, photos = map_profile(views)
            if not photos:
                shutil.rmtree(tmp)
                raise Stop("no photos found - is a profile on screen?")
            question = f"{len(photos)} photos. like?"
        else:
            here = wander(tmp)
            question = f"stopped here, {len(here)} photo(s) on screen. like one?"
        ans = ""
        while ans not in ("y", "n", "q"):
            ans = input(f"{question} [y/n/q] ").strip().lower()
        if ans == "q":
            shutil.rmtree(tmp)
            return
        if ans == "n":
            shutil.rmtree(tmp)
            skip()
            pause(2, 6)
            continue
        comment = random.choice(comments)
        if full:
            which = random.choice(["first", "second", "last"] if len(photos) > 2 else ["first", "last"])
            hy = goto(photos[{"first": 0, "second": 1, "last": -1}[which]], top, views[-1])
        else:
            which, hy = "on-screen", random.choice(here)
        print(f"liking the {which} photo: {comment or 'no comment'!r}")
        rose = send_like(open_sheet(hy, comment))
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        said = f'comment: "{comment}"' if comment else "no comment"
        folder = PEOPLE / time.strftime("%Y-%m-%d_%H%M%S")
        shutil.move(tmp, folder)
        (folder / "profile.md").write_text(
            f"# (not read)\n\nSeen: {ts[:10]} (Discover, tools/hinge.py run)\n\n## Actions\n"
            f"- {ts[:16]}: Priority Like sent on the {which} photo, {said}. "
            f"{'The Rose sheet appeared; Send Like anyway was tapped.' if rose else 'No Rose prompt appeared.'}\n", encoding="utf-8")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{ts}\t{folder.name}\t{which}\t{comment or ''}\n")
        print(f"sent ({liked_today()}/{cap} today), saved to {folder}")
        pause(3, 8)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("shot")
    s = sub.add_parser("scroll")
    s.add_argument("folder", type=Path)
    s = sub.add_parser("like")
    s.add_argument("heart_y", type=int)
    s.add_argument("comment")
    s = sub.add_parser("tap")
    s.add_argument("x", type=int)
    s.add_argument("y", type=int)
    s = sub.add_parser("run")
    s.add_argument("--cap", type=int, default=5)
    s.add_argument("--no-comment", action="store_true")
    s.add_argument("--full", action="store_true")
    a = p.parse_args()

    try:
        if a.cmd == "shot":
            shot()
        elif a.cmd == "scroll":
            scroll(a.folder)
            print(a.folder)
        elif a.cmd == "like":
            open_sheet(a.heart_y / SY, a.comment)
            shot()
        elif a.cmd == "run":
            run(a.cap, a.no_comment, a.full)
        else:
            tap(a.x, a.y)
            shot()
    except Stop as e:
        print(f"stopped: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
