"""Arabic Lohn dub v5: two clearly distinct male voices (deep platform + neutral payroll)."""
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

# A = المنصة يطلب (نبرة عميقة ≈ Mazen)
# B = المحاسبة تنفّذ (نبرة محايدة ≈ Mo)
SEGMENTS = [
    (0.0, 5.5, "A", "النظام متصل. أنا المنصة."),
    (5.5, 12.0, "B", "وأنا نظام المحاسبة. وورك باس لون جاهز."),
    (12.0, 17.0, "A", "حسنًا. اسمع طلبي."),
    (17.0, 24.0, "A", "أرسل لك ساعات العمل والعقود والمناوبات."),
    (24.0, 30.0, "B", "تم. استلمت البيانات."),
    (30.0, 37.0, "A", "الآن انتظر يوم نهاية الشهر."),
    (37.0, 45.0, "B", "مفهوم. أنتظر أمر التشغيل."),
    (45.0, 53.0, "A", "اليوم الثامن والعشرون. افتح الجسر."),
    (53.0, 61.0, "B", "تم. الجسر مفتوح. آمن ومشفّر."),
    (61.0, 70.0, "A", "سلّم البيانات الآن إلى المحاسبة."),
    (70.0, 78.0, "B", "تم التسليم. أبدأ الحساب."),
    (78.0, 90.0, "B", "أحسب الرواتب والتقارير وكشف الحساب وتصدير داتيف."),
    (90.0, 100.0, "A", "بعد الحساب، أرجع النتائج إلى المنصة."),
    (100.0, 110.0, "B", "تم. النتائج عادت بأمان."),
    (110.0, 122.0, "B", "النتيجة جاهزة. متوافقة مع القانون. وآمنة."),
    (122.0, 135.0, "A", "أحسنت. الطلب نُفّذ."),
    (135.0, 150.0, "B", "نظامان. دورة واحدة. الاتصال قائم."),
    (150.0, 158.0, "A", "انتهى. العمل مكتمل."),
]

# صوتان مختلفان تمامًا + إعدادات نبرة منفصلة
VOICE_CFG = {
    "A": {  # deep & professional (Mazen-like)
        "voice": "ar-SA-HamedNeural",
        "rate": "-18%",
        "pitch": "-10Hz",
        "eq": "bass=g=5:f=120,treble=g=-2",
    },
    "B": {  # neutral & professional (Mo-like)
        "voice": "ar-IQ-BasselNeural",
        "rate": "-8%",
        "pitch": "+4Hz",
        "eq": "bass=g=-3:f=120,treble=g=3,highpass=f=90",
    },
}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1500:])


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


async def synth(text: str, speaker: str, out_mp3: Path, out_wav: Path) -> None:
    cfg = VOICE_CFG[speaker]
    await edge_tts.Communicate(
        text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"]
    ).save(str(out_mp3))
    # Convert + EQ so the two speakers stay clearly separable
    run([
        FF, "-y", "-i", str(out_mp3),
        "-ac", "1", "-ar", str(SR),
        "-af", cfg["eq"],
        str(out_wav),
    ])


async def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"missing master: {MASTER}")
    lang_dir = DUB / "ar-v5"
    lang_dir.mkdir(parents=True, exist_ok=True)
    track = np.zeros(int(DURATION * SR) + SR, dtype=np.float32)

    print("A voice:", VOICE_CFG["A"]["voice"], VOICE_CFG["A"]["pitch"])
    print("B voice:", VOICE_CFG["B"]["voice"], VOICE_CFG["B"]["pitch"])

    for i, (start, end, speaker, text) in enumerate(SEGMENTS):
        raw = lang_dir / f"seg_{i:02d}_{speaker}.mp3"
        wav = lang_dir / f"seg_{i:02d}_{speaker}.wav"
        print(f"[{i+1}/{len(SEGMENTS)}] speaker={speaker} voice={VOICE_CFG[speaker]['voice']}")
        await synth(text, speaker, raw, wav)
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        slot = max(0.5, end - start - 0.25)
        max_samples = int(slot * SR)
        if len(audio) > max_samples:
            factor = min(max(len(audio) / max_samples, 1.01), 1.22)
            sped = lang_dir / f"seg_{i:02d}_{speaker}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_samples]

        fade = min(int(0.04 * SR), max(1, len(audio) // 6))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] += audio * 0.98

    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 0.96
    voice = lang_dir / "voice-only.wav"
    write_wav(voice, track)

    out = ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"
    run([
        FF, "-y",
        "-i", str(MASTER),
        "-i", str(voice),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    asyncio.run(main())
