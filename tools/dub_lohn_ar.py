"""Arabic-only Lohn dub with full-frame video and no German audio."""
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

# Natural MSA (light tashkeel) — clearer for neural Arabic TTS
# A = deep platform | B = neutral payroll
SEGMENTS = [
    (0.0, 6.5, "A", "النظام متصل. أنا المنصة."),
    (6.5, 14.0, "B", "أنا وورك باس لون للمحاسبة."),
    (14.0, 18.0, "B", "أسمعك بوضوح."),
    (18.0, 23.0, "A", "وورك باس لون، هل أنت جاهز؟"),
    (23.0, 29.0, "B", "جاهز. أرسل إليّ البيانات."),
    (29.0, 38.0, "A", "أرسل ساعات العمل، والعقود، والمناوبات."),
    (38.0, 44.0, "B", "مفهوم. تم الاستلام."),
    (44.0, 52.0, "B", "أنتظر تشغيل نهاية الشهر."),
    (52.0, 60.0, "A", "اليوم الثامن والعشرون. أفتح الجسر."),
    (60.0, 72.0, "B", "جسر البيانات مفتوح. آمن ومشفّر."),
    (72.0, 84.0, "A", "آتي إليك مع تسليم البيانات."),
    (84.0, 96.0, "B", "مرحبًا بك في عالم وورك باس لون المالي."),
    (96.0, 112.0, "B", "أحسب كشوف الرواتب، والتقارير الرسمية، وكشف الحساب، وتصدير داتيف."),
    (112.0, 128.0, "A", "تعود النتائج بأمان إلى المنصة."),
    (128.0, 142.0, "B", "نتائج ذهبية: جاهزة، ومتوافقة، وآمنة."),
    (142.0, 158.0, "A", "نظامان. دورة واحدة. الاتصال قائم."),
]

VOICES = {
    "A": "ar-SA-HamedNeural",   # deep / professional (platform)
    "B": "ar-AE-HamdanNeural",   # neutral / professional (payroll)
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


async def synth(text: str, voice: str, out: Path) -> None:
    await edge_tts.Communicate(text, voice, rate="-12%").save(str(out))


async def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"missing master: {MASTER}")
    lang_dir = DUB / "ar-v3"
    lang_dir.mkdir(parents=True, exist_ok=True)
    track = np.zeros(int(DURATION * SR) + SR, dtype=np.float32)

    for i, (start, end, speaker, text) in enumerate(SEGMENTS):
        raw = lang_dir / f"seg_{i:02d}.mp3"
        wav = lang_dir / f"seg_{i:02d}.wav"
        print(f"[{i+1}/{len(SEGMENTS)}] {speaker}", text.encode("ascii", "replace").decode("ascii"))
        await synth(text, VOICES[speaker], raw)
        run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), str(wav)])
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        slot = max(0.45, end - start - 0.2)
        max_samples = int(slot * SR)
        if len(audio) > max_samples:
            factor = min(max(len(audio) / max_samples, 1.01), 1.25)
            sped = lang_dir / f"seg_{i:02d}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_samples]

        fade = min(int(0.05 * SR), max(1, len(audio) // 5))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] += audio * 0.98

    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 0.95
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
    print("saved", out, round(out.stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    asyncio.run(main())
