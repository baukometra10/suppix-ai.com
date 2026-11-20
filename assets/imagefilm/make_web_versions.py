"""Create web-optimized ImageFilm + ~25s ad cuts per language."""
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
WEB.mkdir(exist_ok=True)


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-1800:])


def compress(lang: str) -> Path:
    src = ROOT / f"SUPPIX_AI_ImageFilm_{lang}.mp4"
    out = WEB / f"SUPPIX_AI_ImageFilm_{lang}.mp4"
    print(f"compress {lang} ...")
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(src),
            "-vf",
            "scale=-2:720",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "26",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(out),
        ]
    )
    print(f"  -> {out.stat().st_size / 1e6:.1f} MB")
    return out


def make_ad(lang: str, src: Path) -> Path:
    parts = WEB / f"_ad_{lang}"
    parts.mkdir(exist_ok=True)
    # chaos, turn, engine proof, close/demo CTA
    clips = [(0.0, 6.0, "a"), (17.5, 6.0, "b"), (112.0, 8.0, "c"), (175.0, 10.0, "d")]
    files = []
    for ss, dur, name in clips:
        p = parts / f"{name}.mp4"
        fo = max(0.2, dur - 0.25)
        run(
            [
                FFMPEG,
                "-y",
                "-ss",
                f"{ss:.2f}",
                "-i",
                str(src),
                "-t",
                f"{dur:.2f}",
                "-vf",
                f"fade=t=in:st=0:d=0.2,fade=t=out:st={fo:.2f}:d=0.25,fps=24,format=yuv420p",
                "-af",
                f"afade=t=in:d=0.15,afade=t=out:st={fo:.2f}:d=0.25",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "26",
                "-profile:v",
                "main",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                str(p),
            ]
        )
        files.append(p)
    lst = parts / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in files), encoding="utf-8")
    ad = WEB / f"SUPPIX_AI_AD_25s_{lang}.mp4"
    r = subprocess.run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "list.txt",
            "-c",
            "copy",
            str(ad.resolve()),
        ],
        cwd=str(parts),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-1800:])
    print(f"ad {lang} -> {ad.stat().st_size / 1e6:.1f} MB")
    return ad


def main() -> None:
    # poster
    de = ROOT / "SUPPIX_AI_ImageFilm_DE.mp4"
    poster = WEB / "imagefilm-poster.jpg"
    run(
        [
            FFMPEG,
            "-y",
            "-ss",
            "22",
            "-i",
            str(de),
            "-frames:v",
            "1",
            "-q:v",
            "3",
            str(poster),
        ]
    )
    for lang in ("DE", "EN", "AR"):
        web = compress(lang)
        make_ad(lang, web)
    print("DONE")


if __name__ == "__main__":
    main()
