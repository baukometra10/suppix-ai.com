"""
High-quality WorkPass Lohn builds for DE / AR / EN.
- Encode video once from original master (CRF 17, slow)
- Letterbox stretch-fill early scenes (no black bar, no side crop)
- Clearer Arabic male/female dub (slow, short phrases, loudnorm)
"""
from __future__ import annotations

import asyncio
import subprocess
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / "assets" / "lohn-dub"
WHATSAPP = Path(
    r"c:\Users\u4363\Desktop\Screenshots\WhatsApp Video 2026-09-02 at 15 (online-video-cutter.com) (1).mp4"
)
MASTER = DUB / "master-de-src.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
DURATION = 161.5
SR = 44100
SPLIT = 95.0
TOP = 246

# Short clear MSA phrases — request / execute
SEGMENTS_AR = [
    (0.0, 4.5, "A", "النظام متصل."),
    (4.5, 8.5, "A", "أنا المنصة."),
    (8.5, 13.0, "B", "وأنا المحاسبة."),
    (13.0, 17.5, "B", "وورك باس لون جاهزة."),
    (17.5, 22.0, "A", "حسنًا. اسمعي طلبي."),
    (22.0, 29.5, "A", "أرسل لك ساعات العمل. والعقود. والمناوبات."),
    (29.5, 34.5, "B", "تم. استلمت البيانات."),
    (34.5, 40.5, "A", "الآن انتظري يوم نهاية الشهر."),
    (40.5, 46.5, "B", "مفهوم. أنتظر أمر التشغيل."),
    (46.5, 53.5, "A", "اليوم الثامن والعشرون. افتحي الجسر."),
    (53.5, 60.5, "B", "تم. الجسر مفتوح. آمن ومشفّر."),
    (60.5, 68.0, "A", "سلّمي البيانات الآن إلى الحساب."),
    (68.0, 74.0, "B", "تم التسليم. أبدأ الحساب."),
    (74.0, 86.0, "B", "أحسب الرواتب. والتقارير. وكشف الحساب. وتصدير داتيف."),
    (86.0, 94.0, "A", "بعد الحساب. أرجعي النتائج إلى المنصة."),
    (94.0, 101.0, "B", "تم. النتائج عادت بأمان."),
    (101.0, 112.0, "B", "النتيجة جاهزة. متوافقة مع القانون. وآمنة."),
    (112.0, 122.0, "A", "أحسنتِ. الطلب نُفّذ."),
    (122.0, 136.0, "B", "نظامان. دورة واحدة. الاتصال قائم."),
    (136.0, 150.0, "A", "انتهى. العمل مكتمل."),
]

SEGMENTS_EN = [
    (0.0, 4.5, "A", "System online."),
    (4.5, 8.5, "A", "I am the platform."),
    (8.5, 13.0, "B", "And I am payroll accounting."),
    (13.0, 17.5, "B", "WorkPass Lohn is ready."),
    (17.5, 22.0, "A", "Good. Listen to my request."),
    (22.0, 29.5, "A", "I am sending hours. Contracts. And shifts."),
    (29.5, 34.5, "B", "Done. Data received."),
    (34.5, 40.5, "A", "Now wait for month-end."),
    (40.5, 46.5, "B", "Understood. Waiting for the run command."),
    (46.5, 53.5, "A", "Day twenty-eight. Open the bridge."),
    (53.5, 60.5, "B", "Done. Bridge open. Secure and encrypted."),
    (60.5, 68.0, "A", "Hand over the data to accounting now."),
    (68.0, 74.0, "B", "Handover complete. Starting calculation."),
    (74.0, 86.0, "B", "Calculating payslips. Reports. Statements. And DATEV export."),
    (86.0, 94.0, "A", "After calculation. Return results to the platform."),
    (94.0, 101.0, "B", "Done. Results returned securely."),
    (101.0, 112.0, "B", "Result ready. Legally compliant. And secure."),
    (112.0, 122.0, "A", "Well done. Request executed."),
    (122.0, 136.0, "B", "Two systems. One cycle. Connection live."),
    (136.0, 150.0, "A", "Finished. Work complete."),
]

VOICE_AR = {
    "A": {"voice": "ar-SA-HamedNeural", "rate": "-24%", "pitch": "-6Hz"},
    "B": {"voice": "ar-MA-MounaNeural", "rate": "-22%", "pitch": "+0Hz"},
}
VOICE_EN = {
    "A": {"voice": "en-US-GuyNeural", "rate": "-12%", "pitch": "-4Hz"},
    "B": {"voice": "en-GB-SoniaNeural", "rate": "-10%", "pitch": "+0Hz"},
}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1800:])


def ensure_master() -> Path:
    DUB.mkdir(parents=True, exist_ok=True)
    src = WHATSAPP if WHATSAPP.exists() else MASTER
    if not MASTER.exists() or (WHATSAPP.exists() and WHATSAPP.stat().st_mtime > MASTER.stat().st_mtime):
        run([FF, "-y", "-i", str(src), "-c", "copy", str(MASTER)])
        print("master refreshed from", src.name)
    return MASTER


def build_hq_video() -> Path:
    """Single high-quality encode with letterbox stretch-fill for early scenes."""
    master = ensure_master()
    part1 = DUB / "hq-part1.mp4"
    part2 = DUB / "hq-part2.mp4"
    out = DUB / "video-hq.mp4"
    ch = 720 - TOP
    ch -= ch % 2

    common = [
        "-an",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-profile:v", "high",
        "-level", "4.1",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
    ]
    vf1 = f"crop=1280:{ch}:0:{TOP},scale=1280:720:flags=lanczos,setsar=1,unsharp=5:5:0.6:5:5:0.0"
    run([FF, "-y", "-i", str(master), "-t", str(SPLIT), "-vf", vf1, *common, str(part1)])
    run([
        FF, "-y", "-ss", str(SPLIT), "-i", str(master),
        "-vf", "setsar=1,unsharp=5:5:0.4:5:5:0.0",
        *common, str(part2),
    ])
    lst = DUB / "hq-concat.txt"
    lst.write_text(
        f"file '{part1.resolve().as_posix()}'\nfile '{part2.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    # Re-encode concat to one clean stream (avoid timestamp issues) at same HQ
    run([
        FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-preset", "slow", "-crf", "17",
        "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out),
    ])
    print("HQ video", out, round(out.stat().st_size / 1e6, 2), "MB")
    return out


def write_wav(path: Path, samples: np.ndarray, sr: int = SR) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


async def build_voice(lang: str, segments, voices) -> Path:
    lang_dir = DUB / f"{lang}-hq"
    lang_dir.mkdir(parents=True, exist_ok=True)
    track = np.zeros(int(DURATION * SR) + SR, dtype=np.float32)

    for i, (start, end, speaker, text) in enumerate(segments):
        cfg = voices[speaker]
        raw = lang_dir / f"seg_{i:02d}_{speaker}.mp3"
        wav = lang_dir / f"seg_{i:02d}_{speaker}.wav"
        print(f"[{lang} {i+1}/{len(segments)}] {speaker}")
        await edge_tts.Communicate(
            text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"]
        ).save(str(raw))
        run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), str(wav)])
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        slot = max(0.55, end - start - 0.15)
        max_n = int(slot * SR)
        if len(audio) > max_n:
            factor = min(max(len(audio) / max_n, 1.01), 1.15)
            sped = lang_dir / f"seg_{i:02d}_{speaker}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_n]

        fade = min(int(0.05 * SR), max(1, len(audio) // 6))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] += audio * 0.97

    peak = np.max(np.abs(track)) or 1.0
    voice = lang_dir / "voice.wav"
    write_wav(voice, track / peak * 0.92)
    # Broadcast loudness normalize for clear, even speech
    voice_n = lang_dir / "voice-loudnorm.wav"
    run([
        FF, "-y", "-i", str(voice),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=80",
        "-ar", str(SR),
        str(voice_n),
    ])
    return voice_n


def mux(video: Path, audio: Path, out: Path, stereo_from_mono: bool = False) -> None:
    af = "aformat=channel_layouts=stereo" if stereo_from_mono else "anull"
    run([
        FF, "-y",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-af", af,
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


def mux_de(video: Path, master: Path, out: Path) -> None:
    # Keep original German soundtrack, polish lightly
    run([
        FF, "-y",
        "-i", str(video),
        "-i", str(master),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


async def main() -> None:
    video = build_hq_video()
    master = ensure_master()
    mux_de(video, master, ROOT / "assets" / "workpass-lohn-bridge-de.mp4")

    en_voice = await build_voice("en", SEGMENTS_EN, VOICE_EN)
    mux(video, en_voice, ROOT / "assets" / "workpass-lohn-bridge-en.mp4", stereo_from_mono=True)

    ar_voice = await build_voice("ar", SEGMENTS_AR, VOICE_AR)
    mux(video, ar_voice, ROOT / "assets" / "workpass-lohn-bridge-ar.mp4", stereo_from_mono=True)

    run([
        FF, "-y", "-ss", "22",
        "-i", str(ROOT / "assets" / "workpass-lohn-bridge-de.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "2",
        str(ROOT / "assets" / "workpass-lohn-bridge-poster.jpg"),
    ])
    print("poster ok")


if __name__ == "__main__":
    asyncio.run(main())
