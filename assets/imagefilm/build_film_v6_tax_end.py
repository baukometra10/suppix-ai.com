"""Rebuild ImageFilm v6: narration-synced visuals, tax showcase near end, real logo, Marlena-extended VO."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = ROOT / "norm_v6"
VIDEOS = Path(r"c:\Users\u4363\Desktop\Videos")
SITE_VIDEOS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\Videos")

VO = ROOT / "vo_film_marlena_extended.mp3"
LOGO = ROOT / "endcard_logo_real.png"
MUSIC_CANDIDATES = [
    Path(r"c:\Users\u4363\Music\Lux-Inspira Liberation.mp3"),
    Path(r"c:\Users\u4363\Desktop\Lux-Inspira Liberation.mp3"),
    ROOT / "music.mp3",
    ROOT / "music_bed.mp3",
]

# Source clips (already 1920x1080 where possible)
CLIPS = {
    "open": ROOT / "suppix-v4-ots-work.mp4",
    "speak1": ROOT / "suppix-v4-speak.mp4",
    "type": ROOT / "suppix-v4-ots-type.mp4",
    "speak2": ROOT / "suppix-v4-speak2.mp4",
    "employee": ROOT / "employee_app_insert.mp4",
    "portal": ROOT / "ui_portal.mp4",
    "speak3": ROOT / "suppix-v4-speak3.mp4",
    "tax": ROOT / "qr_insert.mp4",  # tax/payroll screen recording
}


def run(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "")[-2000:]
        raise RuntimeError(f"ffmpeg failed ({r.returncode}): {err}")


def normalize(src: Path, dst: Path, seconds: float | None = None, extra_vf: str = "") -> None:
    vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24,format=yuv420p,setsar=1"
    if extra_vf:
        vf = f"{vf},{extra_vf}"
    cmd = [FFMPEG, "-y", "-i", str(src)]
    if seconds is not None:
        cmd += ["-t", f"{seconds:.2f}"]
    cmd += ["-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", str(dst)]
    run(cmd)


def still_logo(dst: Path, seconds: float = 10.0) -> None:
    # Soft fade-in of real company logo on dark plate
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
        "fps=24,format=yuv420p,setsar=1,"
        "fade=t=in:st=0:d=1.2,fade=t=out:st={out:.2f}:d=1.0"
    ).format(out=max(0.5, seconds - 1.0))
    run(
        [
            FFMPEG,
            "-y",
            "-loop",
            "1",
            "-i",
            str(LOGO),
            "-t",
            f"{seconds:.2f}",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dst),
        ]
    )


def tax_showcase(dst: Path, seconds: float = 16.0) -> None:
    # Elegant presentation: fade in/out, hold full UI (no zoom)
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
        "fps=24,format=yuv420p,setsar=1,"
        "fade=t=in:st=0:d=0.9,fade=t=out:st={out:.2f}:d=0.9"
    ).format(out=max(0.5, seconds - 0.9))
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(CLIPS["tax"]),
            "-t",
            f"{seconds:.2f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            str(dst),
        ]
    )


def probe_duration(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            # Duration: HH:MM:SS.xx,
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration for {path}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS.mkdir(parents=True, exist_ok=True)
    SITE_VIDEOS.mkdir(parents=True, exist_ok=True)

    for key, p in CLIPS.items():
        if not p.exists():
            raise SystemExit(f"missing clip {key}: {p}")
    if not VO.exists():
        raise SystemExit(f"missing VO {VO}")
    if not LOGO.exists():
        raise SystemExit(f"missing logo {LOGO}")

    # Beat map aligned to narration order; tax near end before logo
    plan = [
        ("01.mp4", lambda d: normalize(CLIPS["open"], d, 11.0)),
        ("02.mp4", lambda d: normalize(CLIPS["speak1"], d, 12.0)),
        ("03.mp4", lambda d: normalize(CLIPS["speak2"], d, 12.0)),
        ("04.mp4", lambda d: normalize(CLIPS["type"], d, 11.0)),
        ("05.mp4", lambda d: normalize(CLIPS["employee"], d, 22.0)),
        ("06.mp4", lambda d: normalize(CLIPS["portal"], d, 14.0)),
        ("07.mp4", lambda d: normalize(CLIPS["speak3"], d, 12.0)),
        ("08.mp4", lambda d: tax_showcase(d, 16.0)),  # tax / Steuerkette showcase
        ("09.mp4", lambda d: still_logo(d, 10.0)),
    ]

    paths: list[Path] = []
    for name, builder in plan:
        dst = OUT_DIR / name
        print(f"building {name} ...")
        builder(dst)
        paths.append(dst)

    list_file = OUT_DIR / "list.txt"
    list_file.write_text("".join(f"file '{p.name}'\n" for p in paths), encoding="utf-8")
    silent = OUT_DIR / "video_silent.mp4"
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(silent),
        ],
        cwd=str(OUT_DIR),
    )

    vo_dur = probe_duration(VO)
    vid_dur = probe_duration(silent)
    target = max(vo_dur + 1.5, vid_dur)
    print(f"vo={vo_dur:.2f}s video={vid_dur:.2f}s target={target:.2f}s")

    music = next((m for m in MUSIC_CANDIDATES if m.exists()), None)
    final = ROOT / "SUPPIX_AI_ImageFilm_Synced.mp4"

    if music:
        # VO dominant, soft bed music, duck under speech
        filt = (
            f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.0,apad=whole_dur={target}[vo];"
            f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.12,aloop=loop=-1:size=2e9,atrim=0:{target}[mus];"
            f"[vo][mus]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(silent),
                "-i",
                str(VO),
                "-i",
                str(music),
                "-filter_complex",
                filt,
                "-map",
                "0:v",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(final),
            ]
        )
    else:
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(silent),
                "-i",
                str(VO),
                "-filter_complex",
                f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={target}[a]",
                "-map",
                "0:v",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(final),
            ]
        )

    # Easy-to-find copies for the user
    easy = [
        (VO, VIDEOS / "SUPPIX_AI_VO_Marlena_Extended.mp3"),
        (ROOT / "marlena_preview.mp3", VIDEOS / "SUPPIX_AI_VO_Marlena_Preview_Original.mp3"),
        (final, VIDEOS / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (final, SITE_VIDEOS / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (VO, SITE_VIDEOS / "SUPPIX_AI_VO_Marlena_Extended.mp3"),
        (ROOT / "marlena_preview.mp3", SITE_VIDEOS / "SUPPIX_AI_VO_Marlena_Preview_Original.mp3"),
    ]
    for src, dst in easy:
        shutil.copy2(src, dst)
        print(f"copied -> {dst}")

    print(f"DONE {final} ({final.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
