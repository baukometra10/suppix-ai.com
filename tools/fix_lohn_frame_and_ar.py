"""
Fix Lohn video framing (blur-fill letterbox, no content crop) + clearer Arabic dub.
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
MASTER = DUB / "master-de-src.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
DURATION = 161.5
SR = 24000
SPLIT_AT = 95.0
TOP_CROP = 246

# Short phrases + clear pauses for better Arabic articulation
SEGMENTS = [
    (0.0, 5.0, "A", "النظام متصل."),
    (5.0, 9.0, "A", "أنا المنصة."),
    (9.0, 14.5, "B", "وأنا المحاسبة."),
    (14.5, 19.0, "B", "وورك باس لون جاهزة."),
    (19.0, 23.5, "A", "حسنًا. اسمعي طلبي."),
    (23.5, 31.0, "A", "أرسل لك ساعات العمل. والعقود. والمناوبات."),
    (31.0, 36.0, "B", "تم. استلمت البيانات."),
    (36.0, 42.0, "A", "الآن انتظري يوم نهاية الشهر."),
    (42.0, 48.0, "B", "مفهوم. أنتظر أمر التشغيل."),
    (48.0, 55.0, "A", "اليوم الثامن والعشرون. افتحي الجسر."),
    (55.0, 62.0, "B", "تم. الجسر مفتوح. آمن ومشفّر."),
    (62.0, 70.0, "A", "سلّمي البيانات الآن إلى الحساب."),
    (70.0, 76.0, "B", "تم التسليم. أبدأ الحساب."),
    (76.0, 88.0, "B", "أحسب الرواتب. والتقارير. وكشف الحساب. وتصدير داتيف."),
    (88.0, 97.0, "A", "بعد الحساب. أرجعي النتائج إلى المنصة."),
    (97.0, 105.0, "B", "تم. النتائج عادت بأمان."),
    (105.0, 116.0, "B", "النتيجة جاهزة. متوافقة مع القانون. وآمنة."),
    (116.0, 126.0, "A", "أحسنتِ. الطلب نُفّذ."),
    (126.0, 140.0, "B", "نظامان. دورة واحدة. الاتصال قائم."),
    (140.0, 152.0, "A", "انتهى. العمل مكتمل."),
]

VOICE_CFG = {
    "A": {
        "voice": "ar-SA-HamedNeural",
        "rate": "-22%",
        "pitch": "-6Hz",
        "eq": "bass=g=3:f=110",
    },
    "B": {
        "voice": "ar-MA-MounaNeural",
        "rate": "-20%",
        "pitch": "+0Hz",
        "eq": "highpass=f=70,treble=g=1",
    },
}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1800:])


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def build_fullframe_video() -> Path:
    """Early scenes: remove black letterbox via blur-fill (no content crop/zoom)."""
    DUB.mkdir(parents=True, exist_ok=True)
    if not MASTER.exists():
        raise SystemExit(f"missing {MASTER}")

    part1 = DUB / "ff-part1.mp4"
    part2 = DUB / "ff-part2.mp4"
    cleaned = DUB / "video-fullframe.mp4"
    ch = 720 - TOP_CROP
    ch -= ch % 2

    # Foreground keeps full width content; background is blurred scaled fill
    fc = (
        f"[0:v]crop=1280:{ch}:0:{TOP_CROP},split=2[fg][bg];"
        f"[bg]scale=1280:720:force_original_aspect_ratio=increase,"
        f"crop=1280:720,gblur=sigma=18,eq=brightness=-0.08:saturation=0.85[bg2];"
        f"[fg]scale=1280:720:force_original_aspect_ratio=decrease[fg2];"
        f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1"
    )
    run([
        FF, "-y", "-i", str(MASTER), "-t", str(SPLIT_AT),
        "-filter_complex", fc,
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        str(part1),
    ])
    run([
        FF, "-y", "-ss", str(SPLIT_AT), "-i", str(MASTER),
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-vf", "setsar=1",
        str(part2),
    ])
    lst = DUB / "ff-concat.txt"
    lst.write_text(
        f"file '{part1.resolve().as_posix()}'\nfile '{part2.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cleaned)])
    print("fullframe video ready", cleaned)
    return cleaned


async def synth(text: str, speaker: str, out_mp3: Path, out_wav: Path) -> None:
    cfg = VOICE_CFG[speaker]
    await edge_tts.Communicate(
        text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"]
    ).save(str(out_mp3))
    run([
        FF, "-y", "-i", str(out_mp3),
        "-ac", "1", "-ar", str(SR),
        "-af", cfg["eq"],
        str(out_wav),
    ])


async def build_arabic_voice() -> Path:
    lang_dir = DUB / "ar-v7"
    lang_dir.mkdir(parents=True, exist_ok=True)
    track = np.zeros(int(DURATION * SR) + SR, dtype=np.float32)

    for i, (start, end, speaker, text) in enumerate(SEGMENTS):
        raw = lang_dir / f"seg_{i:02d}_{speaker}.mp3"
        wav = lang_dir / f"seg_{i:02d}_{speaker}.wav"
        print(f"[{i+1}/{len(SEGMENTS)}] {speaker}")
        await synth(text, speaker, raw, wav)
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        slot = max(0.55, end - start - 0.2)
        max_samples = int(slot * SR)
        if len(audio) > max_samples:
            factor = min(max(len(audio) / max_samples, 1.01), 1.18)
            sped = lang_dir / f"seg_{i:02d}_{speaker}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_samples]

        fade = min(int(0.045 * SR), max(1, len(audio) // 6))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] += audio * 0.98

    peak = np.max(np.abs(track)) or 1.0
    voice = lang_dir / "voice-only.wav"
    write_wav(voice, track / peak * 0.96)
    return voice


def mux(video: Path, audio: Path | None, out: Path, copy_audio_from: Path | None = None) -> None:
    if audio is not None:
        run([
            FF, "-y", "-i", str(video), "-i", str(audio),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart", str(out),
        ])
    else:
        assert copy_audio_from is not None
        run([
            FF, "-y", "-i", str(video), "-i", str(copy_audio_from),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
            "-shortest", "-movflags", "+faststart", str(out),
        ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


async def main() -> None:
    video = build_fullframe_video()
    # DE keeps original German audio from master
    mux(video, None, ROOT / "assets" / "workpass-lohn-bridge-de.mp4", copy_audio_from=MASTER)
    # EN: keep existing EN voice if present, else remux with silence? Prefer remux existing EN voice track
    en_src = ROOT / "assets" / "workpass-lohn-bridge-en.mp4"
    if en_src.exists():
        en_wav = DUB / "en-extract.wav"
        run([FF, "-y", "-i", str(en_src), "-vn", "-ac", "1", "-ar", str(SR), str(en_wav)])
        mux(video, en_wav, en_src)
    ar_voice = await build_arabic_voice()
    mux(video, ar_voice, ROOT / "assets" / "workpass-lohn-bridge-ar.mp4")
    # poster
    run([
        FF, "-y", "-ss", "22", "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "3",
        str(ROOT / "assets" / "workpass-lohn-bridge-poster.jpg"),
    ])


if __name__ == "__main__":
    asyncio.run(main())
