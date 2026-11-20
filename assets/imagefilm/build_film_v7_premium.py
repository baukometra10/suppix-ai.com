"""Premium ImageFilm v7 — chaos → solution → DE tax film on tax beat → engine → logo.

No website code changes. German master only for now (AR/EN later).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
CURSOR_ASSETS = Path(r"C:\Users\u4363\.cursor\projects\c-Users-u4363-Desktop-Suppix-AI-website\assets")
SITE_ASSETS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\assets")
OUT_DIR = ROOT / "norm_v7"
BEATS_DIR = ROOT / "vo_v7_beats"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
LOGO = ROOT / "endcard_logo_real.png"
FINAL = ROOT / "SUPPIX_AI_ImageFilm_Synced.mp4"
VIDEOS = Path(r"c:\Users\u4363\Desktop\Videos")
SITE_VIDEOS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\Videos")

TAX_DE = SITE_ASSETS / "workpass-lohn-bridge-de.mp4"
# Strong German payroll/tax segment (Abrechnung / Meldewesen / DATEV)
TAX_START = 95.0
TAX_MAX = 32.0


def find(name: str) -> Path:
    for base in (ROOT, CURSOR_ASSETS, SITE_ASSETS):
        p = base / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


def run(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-2500:])


def probe(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration: {path}")


def norm_clip(
    src: Path,
    dst: Path,
    seconds: float,
    *,
    ss: float | None = None,
    fade: bool = True,
    loop_if_short: bool = True,
) -> None:
    """Normalize to 1920x1080@24 with optional fade; loop source if shorter than need."""
    need = max(0.5, seconds)
    src_dur = probe(src)
    inputs: list[str] = [FFMPEG, "-y"]
    if ss is not None:
        inputs += ["-ss", f"{ss:.3f}"]
    if loop_if_short and src_dur + 0.05 < need:
        inputs += ["-stream_loop", "-1"]
    inputs += ["-i", str(src), "-t", f"{need:.3f}"]

    fades = ""
    if fade:
        fi = min(0.55, need * 0.18)
        fo = min(0.55, need * 0.18)
        fades = f",fade=t=in:st=0:d={fi:.2f},fade=t=out:st={max(0.1, need - fo):.2f}:d={fo:.2f}"

    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps=24,format=yuv420p,setsar=1{fades}"
    )
    run(
        inputs
        + [
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


def logo_card(dst: Path, seconds: float = 9.0) -> None:
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
        "fps=24,format=yuv420p,setsar=1,"
        f"fade=t=in:st=0:d=1.1,fade=t=out:st={max(0.5, seconds - 1.0):.2f}:d=1.0"
    )
    run(
        [
            FFMPEG,
            "-y",
            "-loop",
            "1",
            "-i",
            str(LOGO),
            "-t",
            f"{seconds:.3f}",
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


def xfade_pair(a: Path, b: Path, dst: Path, overlap: float = 0.45) -> None:
    da, db = probe(a), probe(b)
    ov = min(overlap, da * 0.25, db * 0.25)
    offset = max(0.05, da - ov)
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(a),
            "-i",
            str(b),
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration={ov:.3f}:offset={offset:.3f},format=yuv420p[v]",
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            str(dst),
        ]
    )


def concat_copy(paths: list[Path], dst: Path) -> None:
    lst = dst.with_suffix(".txt")
    # Relative names — Windows drive paths break ffmpeg concat demuxer quoting
    lines = []
    for p in paths:
        rel = p.name if p.parent == dst.parent else p.resolve().as_posix().replace("'", r"'\''")
        lines.append(f"file '{rel}'\n")
    lst.write_text("".join(lines), encoding="utf-8")
    run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst.name), "-c", "copy", str(dst.name)],
        cwd=str(dst.parent),
    )


def build_visual_for_beat(beat_id: str, seconds: float, dst: Path) -> None:
    """Real motion sources only — no still-image slideshows."""
    chaos_office = find("chaos_office.mp4")
    chaos_apps = find("chaos_apps.mp4")
    solution_calm = find("solution_calm.mp4")
    engine = find("engine_power.mp4")
    robot_ots = find("robot_solution_ots.mp4")
    dash = find("sys_dashboard_motion.mp4")
    livemap = find("sys_livemap_motion.mp4")

    speak = ROOT / "suppix-v4-speak.mp4"
    speak2 = ROOT / "suppix-v4-speak2.mp4"
    speak3 = ROOT / "suppix-v4-speak3.mp4"
    typing = ROOT / "suppix-v4-ots-type.mp4"
    work = ROOT / "suppix-v4-ots-work.mp4"
    employee = ROOT / "employee_app_insert.mp4"

    if beat_id == "01_chaos":
        # Two chaos clips crossfaded to fill narration
        a = OUT_DIR / "_chaos_a.mp4"
        b = OUT_DIR / "_chaos_b.mp4"
        half = max(2.0, seconds / 2 + 0.4)
        norm_clip(chaos_office, a, half)
        norm_clip(chaos_apps, b, half)
        xfade_pair(a, b, dst, 0.5)
        # Trim/pad to exact seconds
        tmp = OUT_DIR / "_chaos_xf.mp4"
        shutil.move(dst, tmp)
        norm_clip(tmp, dst, seconds, loop_if_short=True, fade=False)
        return

    if beat_id == "02_turn":
        a = OUT_DIR / "_turn_a.mp4"
        b = OUT_DIR / "_turn_b.mp4"
        norm_clip(solution_calm, a, seconds * 0.55 + 0.4)
        norm_clip(speak if speak.exists() else robot_ots, b, seconds * 0.55 + 0.4)
        xfade_pair(a, b, dst, 0.45)
        tmp = OUT_DIR / "_turn_xf.mp4"
        shutil.move(dst, tmp)
        norm_clip(tmp, dst, seconds, fade=False)
        return

    if beat_id == "03_platform":
        a = OUT_DIR / "_plat_a.mp4"
        b = OUT_DIR / "_plat_b.mp4"
        norm_clip(work if work.exists() else robot_ots, a, seconds * 0.55 + 0.3)
        norm_clip(dash, b, seconds * 0.55 + 0.3)
        xfade_pair(a, b, dst, 0.4)
        tmp = OUT_DIR / "_plat_xf.mp4"
        shutil.move(dst, tmp)
        norm_clip(tmp, dst, seconds, fade=False)
        return

    if beat_id == "04_contract":
        norm_clip(typing if typing.exists() else robot_ots, dst, seconds)
        return

    if beat_id == "05_employee":
        norm_clip(employee, dst, seconds, ss=0.0)
        return

    if beat_id == "06_ops":
        a = OUT_DIR / "_ops_a.mp4"
        b = OUT_DIR / "_ops_b.mp4"
        norm_clip(livemap, a, seconds * 0.55 + 0.3)
        norm_clip(speak2 if speak2.exists() else dash, b, seconds * 0.55 + 0.3)
        xfade_pair(a, b, dst, 0.4)
        tmp = OUT_DIR / "_ops_xf.mp4"
        shutil.move(dst, tmp)
        norm_clip(tmp, dst, seconds, fade=False)
        return

    if beat_id == "07_tax":
        # German tax / Lohn bridge film — appears exactly on tax narration
        if not TAX_DE.exists():
            raise FileNotFoundError(TAX_DE)
        norm_clip(TAX_DE, dst, min(seconds, TAX_MAX), ss=TAX_START, loop_if_short=True, fade=True)
        return

    if beat_id == "08_engine":
        norm_clip(engine, dst, seconds)
        return

    if beat_id == "09_close":
        # speak closing then real logo
        speak_dur = max(3.0, seconds * 0.55)
        logo_dur = max(4.0, seconds - speak_dur + 0.5)
        a = OUT_DIR / "_close_speak.mp4"
        b = OUT_DIR / "_close_logo.mp4"
        norm_clip(speak3 if speak3.exists() else speak, a, speak_dur)
        logo_card(b, logo_dur)
        xfade_pair(a, b, dst, 0.6)
        tmp = OUT_DIR / "_close_xf.mp4"
        shutil.move(dst, tmp)
        norm_clip(tmp, dst, seconds, fade=False)
        return

    raise KeyError(beat_id)


def mux(video: Path, audio: Path, music: Path | None, dst: Path) -> None:
    vd = probe(video)
    ad = probe(audio)
    target = max(vd, ad) + 0.4
    if music and music.exists():
        filt = (
            f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.05,"
            f"apad=whole_dur={target}[vo];"
            f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.10,"
            f"aloop=loop=-1:size=2e9,atrim=0:{target}[mus];"
            f"[vo][mus]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(video),
                "-i",
                str(audio),
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
                "17",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(dst),
            ]
        )
    else:
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(video),
                "-i",
                str(audio),
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
                "17",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(dst),
            ]
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS.mkdir(parents=True, exist_ok=True)
    SITE_VIDEOS.mkdir(parents=True, exist_ok=True)

    beats_path = BEATS_DIR / "beats.json"
    if not beats_path.exists():
        raise SystemExit("Run make_vo_v7_beats.py first")
    beats = json.loads(beats_path.read_text(encoding="utf-8"))

    # Copy fresh generated assets into imagefilm for permanence
    for name in (
        "chaos_office.mp4",
        "chaos_apps.mp4",
        "solution_calm.mp4",
        "engine_power.mp4",
        "sys_dashboard_motion.mp4",
        "sys_livemap_motion.mp4",
        "robot_solution_ots.mp4",
    ):
        src = find(name)
        dst = ROOT / name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)

    visual_parts: list[Path] = []
    audio_parts: list[Path] = []
    for b in beats:
        bid = b["id"]
        dur = float(b["duration"]) + 0.25  # small breathing room after each line
        # Tax beat: keep visual at least as long as strong tax segment needs
        if bid == "07_tax":
            dur = max(dur, min(TAX_MAX, dur + 2.0))
        if bid == "09_close":
            dur = max(dur, float(b["duration"]) + 3.5)  # hold logo

        vdst = OUT_DIR / f"{bid}.mp4"
        print(f"visual {bid} ({dur:.2f}s) ...")
        build_visual_for_beat(bid, dur, vdst)
        # Re-time exactly
        exact = OUT_DIR / f"{bid}_exact.mp4"
        norm_clip(vdst, exact, dur, fade=False, loop_if_short=True)
        visual_parts.append(exact)
        audio_parts.append(BEATS_DIR / b["file"])

    # Pad each audio to match its visual duration with silence
    aligned_audio: list[Path] = []
    for b, vpath, apath in zip(beats, visual_parts, audio_parts):
        vd = probe(vpath)
        ad = probe(apath)
        out_a = OUT_DIR / f"a_{b['id']}.wav"
        pad = max(0.0, vd - ad)
        if pad > 0.05:
            run(
                [
                    FFMPEG,
                    "-y",
                    "-i",
                    str(apath),
                    "-af",
                    f"apad=pad_dur={pad:.3f}",
                    "-ar",
                    "44100",
                    "-ac",
                    "1",
                    str(out_a),
                ]
            )
        else:
            run(
                [
                    FFMPEG,
                    "-y",
                    "-i",
                    str(apath),
                    "-t",
                    f"{vd:.3f}",
                    "-ar",
                    "44100",
                    "-ac",
                    "1",
                    str(out_a),
                ]
            )
        aligned_audio.append(out_a)

    silent = OUT_DIR / "video_silent.mp4"
    voice = OUT_DIR / "voice_aligned.wav"
    concat_copy(visual_parts, silent)
    # concat audio
    alist = OUT_DIR / "audio_list.txt"
    alist.write_text("".join(f"file '{p.name}'\n" for p in aligned_audio), encoding="utf-8")
    run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "audio_list.txt", "-c", "copy", "voice_aligned.wav"],
        cwd=str(OUT_DIR),
    )

    music = ROOT / "music_bed.mp3"
    if not music.exists():
        music = None
    mux(silent, voice, music, FINAL)

    easy = [
        (FINAL, VIDEOS / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (FINAL, SITE_VIDEOS / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (ROOT / "vo_v7_premium_full.mp3", VIDEOS / "SUPPIX_AI_VO_DE_Premium.mp3"),
        (ROOT / "vo_v7_premium_full.mp3", SITE_VIDEOS / "SUPPIX_AI_VO_DE_Premium.mp3"),
    ]
    for src, dst in easy:
        if src.exists():
            shutil.copy2(src, dst)
            print(f"copied {dst}")

    print(f"DONE {FINAL} video={probe(FINAL):.2f}s size={FINAL.stat().st_size}")


if __name__ == "__main__":
    main()
