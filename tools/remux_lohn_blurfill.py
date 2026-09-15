"""Remove authored top letterbox: mild vertical fit + visible blur fill (no side crop)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / "assets" / "lohn-dub"
MASTER = DUB / "master-de-src.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1800:])


def encode_segment(src: Path, out: Path, top: int, duration: float | None, ss: float | None) -> None:
    ch = 720 - top
    ch -= ch % 2
    # Foreground: mild height lift (474→640) shrinks empty pad without full stretch-to-720.
    # Background: brightened blur so pads never look like a dead black void.
    fg_h = min(640, 720)
    fg_h -= fg_h % 2
    fc = (
        f"[0:v]crop=1280:{ch}:0:{top},split=2[fg][bg];"
        f"[bg]scale=1280:720,gblur=sigma=28,"
        f"eq=brightness=0.14:saturation=1.15:contrast=1.05[bg2];"
        f"[fg]scale=1280:{fg_h}[fg2];"
        f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1"
    )
    cmd = [FF, "-y"]
    if ss is not None:
        cmd += ["-ss", str(ss)]
    cmd += ["-i", str(src)]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += [
        "-filter_complex", fc, "-an",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
        str(out),
    ]
    run(cmd)


def main() -> None:
    part1 = DUB / "blur-part1.mp4"
    part2 = DUB / "blur-part2.mp4"
    cleaned = DUB / "video-blurfill.mp4"

    print("encoding part1 (top=246)...")
    encode_segment(MASTER, part1, top=246, duration=95.0, ss=None)
    print("encoding part2 (top=40)...")
    encode_segment(MASTER, part2, top=40, duration=None, ss=95.0)

    lst = DUB / "blur-concat.txt"
    lst.write_text(
        f"file '{part1.resolve().as_posix()}'\nfile '{part2.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cleaned)])
    print("cleaned", round(cleaned.stat().st_size / 1e6, 2), "MB")

    for lang in ("de", "en", "ar"):
        src = ROOT / "assets" / f"workpass-lohn-bridge-{lang}.mp4"
        out = ROOT / "assets" / f"workpass-lohn-bridge-{lang}.mp4"
        tmp = DUB / f"tmp-a-{lang}.m4a"
        run([FF, "-y", "-i", str(src), "-vn", "-c:a", "aac", "-b:a", "192k", str(tmp)])
        run([
            FF, "-y", "-i", str(cleaned), "-i", str(tmp),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "copy",
            "-shortest", "-movflags", "+faststart", str(out),
        ])
        print(lang, round(out.stat().st_size / 1e6, 2), "MB")

    run([
        FF, "-y", "-ss", "28",
        "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "2",
        str(ROOT / "assets" / "workpass-lohn-bridge-poster.jpg"),
    ])

    for t in (9, 28, 60, 120):
        shot = DUB / f"_blurcheck_{t}.jpg"
        run([
            FF, "-y", "-ss", str(t),
            "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
            "-frames:v", "1", "-update", "1", "-q:v", "3", str(shot),
        ])
        g = np.array(Image.open(shot).convert("RGB")).mean(axis=2)
        top = next((y for y in range(min(200, g.shape[0])) if g[y].mean() > 18), 0)
        print(f"t={t} dark_top≈{top}")
    print("done")


if __name__ == "__main__":
    main()
