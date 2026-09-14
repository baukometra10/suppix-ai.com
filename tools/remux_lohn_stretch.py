"""Stretch-fill letterbox (no black, no side crop) and remux DE/EN/AR audio."""
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / "assets" / "lohn-dub"
MASTER = DUB / "master-de-src.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SPLIT = 95.0
TOP = 246


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1500:])


def main():
    ch = 720 - TOP
    ch -= ch % 2
    part1 = DUB / "ff-part1.mp4"
    part2 = DUB / "ff-part2.mp4"
    cleaned = DUB / "video-fullframe.mp4"

    vf1 = f"crop=1280:{ch}:0:{TOP},scale=1280:720,setsar=1"
    run([
        FF, "-y", "-i", str(MASTER), "-t", str(SPLIT),
        "-vf", vf1, "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        str(part1),
    ])
    run([
        FF, "-y", "-ss", str(SPLIT), "-i", str(MASTER),
        "-an", "-vf", "setsar=1",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        str(part2),
    ])
    lst = DUB / "ff-concat.txt"
    lst.write_text(
        f"file '{part1.resolve().as_posix()}'\nfile '{part2.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cleaned)])
    print("clean ok")

    for lang, src_audio in [
        ("de", MASTER),
        ("en", ROOT / "assets" / "workpass-lohn-bridge-en.mp4"),
        ("ar", ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
    ]:
        out = ROOT / "assets" / f"workpass-lohn-bridge-{lang}.mp4"
        tmp = DUB / f"tmp-audio-{lang}.m4a"
        run([FF, "-y", "-i", str(src_audio), "-vn", "-c:a", "aac", "-b:a", "192k", str(tmp)])
        run([
            FF, "-y", "-i", str(cleaned), "-i", str(tmp),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "copy",
            "-shortest", "-movflags", "+faststart", str(out),
        ])
        print(lang, round(out.stat().st_size / 1e6, 2), "MB")

    for t in (5, 22, 50):
        shot = DUB / f"_v3_{t}.jpg"
        run([
            FF, "-y", "-ss", str(t), "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
            "-frames:v", "1", "-update", "1", "-q:v", "3", str(shot),
        ])
        g = np.array(Image.open(shot).convert("RGB")).mean(axis=2)
        top = next((y for y in range(g.shape[0]) if g[y].mean() > 12), 0)
        print("t", t, "topbar", top)

    run([
        FF, "-y", "-ss", "22", "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "3",
        str(ROOT / "assets" / "workpass-lohn-bridge-poster.jpg"),
    ])
    print("poster ok")


if __name__ == "__main__":
    main()
