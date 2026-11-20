"""ImageFilm v8 — excitement pack: pacing, grade, SFX, music arc, month-end cinema, proof beat."""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
CURSOR = Path(r"C:\Users\u4363\.cursor\projects\c-Users-u4363-Desktop-Suppix-AI-website\assets")
SITE = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\assets")
OUT = ROOT / "norm_v8"
BEATS = ROOT / "vo_v8_beats"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
LOGO = ROOT / "endcard_logo_real.png"
TAX_DE = SITE / "workpass-lohn-bridge-de.mp4"
FINAL = ROOT / "SUPPIX_AI_ImageFilm_Synced.mp4"
PLAY = ROOT / "SUPPIX_AI_ImageFilm_PLAY.mp4"
VIDEOS = Path(r"c:\Users\u4363\Desktop\Videos")
SITE_VIDEOS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\Videos")
DESKTOP = Path(r"c:\Users\u4363\Desktop")

TAX_SS = 100.0  # strong Steuer/Lohn stretch


def find(name: str) -> Path:
    for b in (ROOT, CURSOR, SITE):
        p = b / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


def run(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-3000:])


def probe(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"duration: {path}")


def make_sfx() -> dict[str, Path]:
    """Synthetic whoosh / hit / riser — no external library needed."""
    sfx_dir = OUT / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    specs = {
        "whoosh": (
            "sine=f=900:d=0.35,afade=t=in:d=0.05,afade=t=out:d=0.25,volume=0.25;"
            "sine=f=220:d=0.35,afade=t=in:d=0.02,afade=t=out:d=0.3,volume=0.2"
        ),
        "hit": "sine=f=80:d=0.18,afade=t=out:d=0.16,volume=0.45",
        "riser": "sine=f=200:d=1.2,afade=t=in:d=1.0,afade=t=out:d=0.2,volume=0.18",
        "success": "sine=f=660:d=0.25,afade=t=out:d=0.2,volume=0.22",
    }
    # simpler single-source generators
    outs = {}
    cmds = {
        "whoosh": f"anoisesrc=color=pink:d=0.4,highpass=f=400,lowpass=f=4000,afade=t=in:d=0.05,afade=t=out:d=0.25,volume=0.35",
        "hit": f"sine=frequency=70:duration=0.2,afade=t=out:st=0:d=0.2,volume=0.5",
        "riser": f"sine=frequency=180:duration=1.1,afade=t=in:st=0:d=1.0,volume=0.2",
        "success": f"sine=frequency=740:duration=0.28,afade=t=out:st=0:d=0.25,volume=0.28",
    }
    for name, expr in cmds.items():
        p = sfx_dir / f"{name}.wav"
        run(
            [
                FFMPEG,
                "-y",
                "-f",
                "lavfi",
                "-i",
                expr,
                "-ar",
                "44100",
                "-ac",
                "2",
                str(p),
            ]
        )
        outs[name] = p
    return outs


def grade_vf(kind: str, seconds: float, fade: bool = True) -> str:
    """Visual contrast: chaos cold/dense vs solution clean/bright."""
    base = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24,format=yuv420p,setsar=1"
    )
    if kind == "chaos":
        # colder, slightly crushed, denser contrast
        base += ",eq=contrast=1.18:brightness=-0.06:saturation=0.72,colorbalance=bs=0.08:bh=0.04"
        # subtle urgency via mild unsharp
        base += ",unsharp=5:5:0.6:5:5:0.0"
    elif kind == "solution":
        base += ",eq=contrast=1.05:brightness=0.04:saturation=1.05,colorbalance=rs=0.02:gs=0.02:bs=-0.02"
    elif kind == "tax":
        base += ",eq=contrast=1.08:brightness=0.02:saturation=1.08"
    elif kind == "engine":
        base += ",eq=contrast=1.12:brightness=0.03:saturation=1.1,colorbalance=bs=0.05:gs=0.02"
    elif kind == "proof":
        # keep room for drawtext overlay clarity
        base += ",eq=contrast=1.1:brightness=0.05:saturation=1.05"
    else:
        base += ",eq=contrast=1.06:brightness=0.02:saturation=1.02"

    if fade:
        fi = min(0.35, seconds * 0.12)
        fo = min(0.35, seconds * 0.12)
        base += f",fade=t=in:st=0:d={fi:.2f},fade=t=out:st={max(0.05, seconds - fo):.2f}:d={fo:.2f}"
    return base


def norm(
    src: Path,
    dst: Path,
    seconds: float,
    *,
    kind: str = "solution",
    ss: float | None = None,
    loop_if_short: bool = True,
    fade: bool = True,
    extra_vf: str = "",
) -> None:
    need = max(0.4, seconds)
    src_dur = probe(src)
    cmd = [FFMPEG, "-y"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    if loop_if_short and src_dur + 0.08 < need:
        cmd += ["-stream_loop", "-1"]
    cmd += ["-i", str(src), "-t", f"{need:.3f}"]
    vf = grade_vf(kind, need, fade=fade)
    if extra_vf:
        vf += "," + extra_vf
    cmd += [
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
        "-profile:v",
        "main",
        str(dst),
    ]
    run(cmd)


def logo_card(dst: Path, seconds: float) -> None:
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24,format=yuv420p,setsar=1,"
        f"fade=t=in:st=0:d=1.0,fade=t=out:st={max(0.4, seconds - 1.1):.2f}:d=1.0"
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
            "-profile:v",
            "main",
            "-an",
            str(dst),
        ]
    )


def xfade(a: Path, b: Path, dst: Path, overlap: float = 0.35) -> None:
    da, db = probe(a), probe(b)
    ov = min(overlap, da * 0.2, db * 0.2)
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
            "-profile:v",
            "main",
            str(dst),
        ]
    )


def proof_overlay(src: Path, dst: Path, seconds: float) -> None:
    """Cinematic proof beat: 100.000 Mitarbeitende / 115 Sekunden."""
    # Draw large centered proof lines mid-clip
    # Fontfile optional — use default
    start = max(0.4, seconds * 0.22)
    dur = min(4.5, seconds * 0.55)
    text1 = "100.000 Mitarbeitende"
    text2 = "115 Sekunden"
    # escape for ffmpeg drawtext
    def esc(t: str) -> str:
        return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    draw = (
        f"drawtext=text='{esc(text1)}':fontsize=64:fontcolor=white:borderw=3:bordercolor=black@0.55:"
        f"x=(w-text_w)/2:y=(h*0.38):enable='between(t\\,{start:.2f}\\,{start + dur:.2f})',"
        f"drawtext=text='{esc(text2)}':fontsize=78:fontcolor=0x7DD3FC:borderw=3:bordercolor=black@0.55:"
        f"x=(w-text_w)/2:y=(h*0.50):enable='between(t\\,{start:.2f}\\,{start + dur:.2f})'"
    )
    norm(src, dst, seconds, kind="proof", fade=True, extra_vf=draw)


def build_visual(beat_id: str, seconds: float, dst: Path) -> None:
    chaos_office = find("chaos_office.mp4")
    chaos_apps = find("chaos_apps.mp4")
    chaos_to = find("chaos_to_solution.mp4")
    solution = find("solution_calm.mp4")
    monthend = find("monthend_flow.mp4")
    accounting = find("accounting_process.mp4")
    dispatch = find("payslip_dispatch.mp4")
    engine = find("engine_power.mp4")
    dash = find("sys_dashboard_motion.mp4")
    livemap = find("sys_livemap_motion.mp4")
    speak = ROOT / "suppix-v4-speak.mp4"
    speak2 = ROOT / "suppix-v4-speak2.mp4"
    speak3 = ROOT / "suppix-v4-speak3.mp4"
    typing = ROOT / "suppix-v4-ots-type.mp4"
    work = ROOT / "suppix-v4-ots-work.mp4"
    employee = ROOT / "employee_app_insert.mp4"

    def xf_trim(a_src: Path, b_src: Path, ka: str, kb: str) -> None:
        a = OUT / f"_{beat_id}_a.mp4"
        b = OUT / f"_{beat_id}_b.mp4"
        half = seconds / 2 + 0.45
        norm(a_src, a, half, kind=ka)
        norm(b_src, b, half, kind=kb)
        mid = OUT / f"_{beat_id}_xf.mp4"
        xfade(a, b, mid, 0.32)
        norm(mid, dst, seconds, kind=kb, fade=False, loop_if_short=True)

    if beat_id == "01_chaos":
        # Faster pacing: three quick punches via two xfades conceptually — office then apps hard
        a = OUT / "_c1.mp4"
        b = OUT / "_c2.mp4"
        # shorter pieces, snappier fades
        norm(chaos_office, a, max(2.2, seconds * 0.48), kind="chaos", fade=True)
        norm(chaos_apps, b, max(2.2, seconds * 0.58), kind="chaos", fade=True)
        mid = OUT / "_c_xf.mp4"
        xfade(a, b, mid, 0.22)
        norm(mid, dst, seconds, kind="chaos", fade=False)
        return

    if beat_id == "02_turn":
        a = OUT / "_t1.mp4"
        b = OUT / "_t2.mp4"
        norm(chaos_to, a, seconds * 0.42 + 0.3, kind="chaos")
        norm(speak if speak.exists() else solution, b, seconds * 0.65 + 0.3, kind="solution")
        mid = OUT / "_t_xf.mp4"
        xfade(a, b, mid, 0.28)
        norm(mid, dst, seconds, kind="solution", fade=False)
        return

    if beat_id == "03_platform":
        xf_trim(work if work.exists() else solution, dash, "solution", "solution")
        return

    if beat_id == "04_contract":
        norm(typing if typing.exists() else work, dst, seconds, kind="solution")
        return

    if beat_id == "05_employee":
        norm(employee, dst, seconds, kind="solution")
        return

    if beat_id == "06_ops":
        xf_trim(livemap, speak2 if speak2.exists() else dash, "solution", "solution")
        return

    if beat_id == "07_tax":
        if not TAX_DE.exists():
            raise FileNotFoundError(TAX_DE)
        norm(TAX_DE, dst, seconds, kind="tax", ss=TAX_SS, loop_if_short=True)
        return

    if beat_id == "08_monthend":
        a = OUT / "_me_a.mp4"
        b = OUT / "_me_b.mp4"
        norm(monthend, a, seconds * 0.55 + 0.4, kind="engine")
        if TAX_DE.exists():
            norm(TAX_DE, b, seconds * 0.55 + 0.4, kind="tax", ss=120.0)
        else:
            norm(accounting, b, seconds * 0.55 + 0.4, kind="engine")
        mid = OUT / "_me_xf.mp4"
        xfade(a, b, mid, 0.4)
        norm(mid, dst, seconds, kind="tax", fade=False)
        return

    if beat_id == "09_engine":
        # Process clip + proof numbers
        tmp = OUT / "_engine_raw.mp4"
        a = OUT / "_eng_a.mp4"
        b = OUT / "_eng_b.mp4"
        norm(accounting, a, seconds * 0.55 + 0.5, kind="engine")
        norm(engine, b, seconds * 0.55 + 0.5, kind="engine")
        xfade(a, b, tmp, 0.35)
        proof_overlay(tmp, dst, seconds)
        return

    if beat_id == "10_dispatch":
        norm(dispatch, dst, seconds, kind="solution")
        return

    if beat_id == "11_close":
        speak_dur = max(4.0, min(seconds * 0.45, seconds - 5.5))
        logo_dur = max(5.5, seconds - speak_dur + 0.6)
        a = OUT / "_cl_s.mp4"
        b = OUT / "_cl_l.mp4"
        norm(speak3 if speak3.exists() else speak, a, speak_dur, kind="solution")
        logo_card(b, logo_dur)
        mid = OUT / "_cl_xf.mp4"
        xfade(a, b, mid, 0.7)
        norm(mid, dst, seconds, kind="solution", fade=False)
        return

    raise KeyError(beat_id)


def concat_rel(paths: list[Path], dst: Path) -> None:
    lst = dst.with_name(dst.stem + "_list.txt")
    lst.write_text("".join(f"file '{p.name}'\n" for p in paths), encoding="utf-8")
    run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst.name, "-c", "copy", dst.name],
        cwd=str(dst.parent),
    )


def music_filter(total: float) -> str:
    """Volume envelope: tense chaos → lift solution → proud end."""
    # chaos ~ first 18s low-mid tense; solution rise; engine peak; end soft proud
    return (
        f"aformat=sample_rates=44100:channel_layouts=stereo,"
        f"volume=0.11,"
        f"afade=t=in:st=0:d=1.5,"
        f"volume='if(lt(t,18),0.13,if(lt(t,55),0.10,if(lt(t,110),0.12,0.09)))':eval=frame,"
        f"aloop=loop=-1:size=2e9,atrim=0:{total:.3f}"
    )


def mix_final(video: Path, voice: Path, music: Path | None, sfx: dict[str, Path], transitions: list[float], dst: Path) -> None:
    vd = probe(video)
    target = vd + 0.25
    # Build filter: voice + music + sfx at transition times
    inputs = [FFMPEG, "-y", "-i", str(video), "-i", str(voice)]
    idx = 2
    sfx_chain = []
    if music and music.exists():
        inputs += ["-i", str(music)]
        mus_i = idx
        idx += 1
    else:
        mus_i = None

    whoosh_i = hit_i = success_i = None
    for key in ("whoosh", "hit", "success"):
        inputs += ["-i", str(sfx[key])]
        if key == "whoosh":
            whoosh_i = idx
        elif key == "hit":
            hit_i = idx
        else:
            success_i = idx
        idx += 1

    # Place SFX near major transitions (seconds into timeline)
    parts = [f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.08,apad=whole_dur={target}[vo]"]
    mix_inputs = ["[vo]"]
    n = 1
    if mus_i is not None:
        parts.append(f"[{mus_i}:a]{music_filter(target)}[mus]")
        mix_inputs.append("[mus]")
        n += 1

    # Schedule whoosh/hit on transitions
    for i, t in enumerate(transitions):
        lab = f"sx{i}"
        src_i = whoosh_i if i % 2 == 0 else hit_i
        delay_ms = int(max(0, t) * 1000)
        parts.append(
            f"[{src_i}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
            f"volume=0.55,adelay={delay_ms}|{delay_ms},apad=whole_dur={target}[{lab}]"
        )
        mix_inputs.append(f"[{lab}]")
        n += 1

    # Success sting near engine proof (~ after monthend+tax) — use last third
    if success_i is not None and transitions:
        st = transitions[-2] if len(transitions) >= 2 else target * 0.7
        delay_ms = int(st * 1000)
        parts.append(
            f"[{success_i}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
            f"volume=0.4,adelay={delay_ms}|{delay_ms},apad=whole_dur={target}[succ]"
        )
        mix_inputs.append("[succ]")
        n += 1

    parts.append(
        "".join(mix_inputs)
        + f"amix=inputs={n}:duration=first:dropout_transition=2:normalize=0[a]"
    )
    filt = ";".join(parts)

    run(
        inputs
        + [
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
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
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
    OUT.mkdir(parents=True, exist_ok=True)
    VIDEOS.mkdir(parents=True, exist_ok=True)
    SITE_VIDEOS.mkdir(parents=True, exist_ok=True)

    # Persist generated clips
    for name in (
        "monthend_flow.mp4",
        "accounting_process.mp4",
        "payslip_dispatch.mp4",
        "chaos_to_solution.mp4",
    ):
        src = find(name)
        dst = ROOT / name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)

    beats = json.loads((BEATS / "beats.json").read_text(encoding="utf-8"))
    sfx = make_sfx()

    # Duration policy for excitement
    pads = {
        "01_chaos": 0.05,  # snappy
        "02_turn": 0.2,
        "03_platform": 0.2,
        "04_contract": 0.15,
        "05_employee": 0.15,
        "06_ops": 0.15,
        "07_tax": 1.0,
        "08_monthend": 0.8,
        "09_engine": 1.2,  # proof hold
        "10_dispatch": 0.6,
        "11_close": 4.0,  # stronger logo
    }

    visuals = []
    audios = []
    transitions = []
    t_cursor = 0.0

    for b in beats:
        bid = b["id"]
        dur = float(b["duration"]) + pads.get(bid, 0.2)
        if bid == "01_chaos":
            dur = min(dur, float(b["duration"]) + 0.05)  # keep tight
        print(f"visual {bid} {dur:.2f}s @ {t_cursor:.1f}s")
        if t_cursor > 0.5:
            transitions.append(t_cursor)
        vpath = OUT / f"{bid}.mp4"
        build_visual(bid, dur, vpath)
        exact = OUT / f"{bid}_exact.mp4"
        # final timebase lock without re-grading harshly
        run(
            [
                FFMPEG,
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(vpath),
                "-t",
                f"{dur:.3f}",
                "-vf",
                "fps=24,format=yuv420p,setsar=1",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "17",
                "-profile:v",
                "main",
                str(exact),
            ]
        )
        visuals.append(exact)

        # align audio
        apath = BEATS / b["file"]
        vd = probe(exact)
        ad = probe(apath)
        out_a = OUT / f"a_{bid}.wav"
        pad = max(0.0, vd - ad)
        if pad > 0.04:
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
        audios.append(out_a)
        t_cursor += vd

    silent = OUT / "video_silent.mp4"
    voice = OUT / "voice_aligned.wav"
    concat_rel(visuals, silent)
    alist = OUT / "audio_list.txt"
    alist.write_text("".join(f"file '{p.name}'\n" for p in audios), encoding="utf-8")
    run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "audio_list.txt", "-c", "copy", "voice_aligned.wav"],
        cwd=str(OUT),
    )

    music = ROOT / "music_bed.mp3"
    mix_final(silent, voice, music if music.exists() else None, sfx, transitions, FINAL)

    # Windows-friendly play copy
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(FINAL),
            "-c:v",
            "libx264",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(PLAY),
        ]
    )

    vo_full = ROOT / "vo_v8_premium_full.mp3"
    copies = [
        (PLAY, VIDEOS / "SUPPIX_AI_ImageFilm_PLAY.mp4"),
        (PLAY, VIDEOS / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (PLAY, SITE_VIDEOS / "SUPPIX_AI_ImageFilm_PLAY.mp4"),
        (PLAY, SITE_VIDEOS / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (PLAY, ROOT / "SUPPIX_AI_ImageFilm_Synced.mp4"),
        (vo_full, VIDEOS / "SUPPIX_AI_VO_DE_Premium.mp3"),
        (vo_full, SITE_VIDEOS / "SUPPIX_AI_VO_DE_Premium.mp3"),
    ]
    for src, dst in copies:
        if src.exists():
            shutil.copy2(src, dst)
            print("copied", dst)

    # short preview on desktop
    preview = DESKTOP / "SUPPIX_AI_PREVIEW_12s.mp4"
    run(
        [
            FFMPEG,
            "-y",
            "-ss",
            "4",
            "-i",
            str(PLAY),
            "-t",
            "12",
            "-c:v",
            "libx264",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(preview),
        ]
    )
    print(f"DONE {PLAY} {probe(PLAY):.2f}s {PLAY.stat().st_size} bytes")


if __name__ == "__main__":
    main()
