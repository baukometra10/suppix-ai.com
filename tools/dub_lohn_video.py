"""
Build Arabic + English dubbed WorkPass Lohn videos from DE master.
Uses timed dialogue scripts + edge-tts, keeps original music bed low.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / "assets" / "lohn-dub"
SRC_VIDEO = ROOT / "assets" / "workpass-lohn-bridge-de.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
DURATION = 161.5  # seconds

# Two speakers: platform + payroll
# Timings aligned to scenes in the DE master.
SEGMENTS = [
    # start, end, speaker (A=platform, B=lohn), de, en, ar
    (0.0, 6.5, "A",
     "System online. Ich bin die Plattform.",
     "System online. I am the platform.",
     "النظام متصل. أنا المنصة."),
    (6.5, 14.5, "B",
     "Ich bin WorkPass Lohn.",
     "I am WorkPass Lohn.",
     "أنا وورك باس لون للمحاسبة."),
    (14.5, 18.0, "B",
     "Ich höre dich.",
     "I hear you.",
     "أسمعك."),
    (18.0, 22.0, "A",
     "WorkPass Lohn — bereit?",
     "WorkPass Lohn — ready?",
     "وورك باس لون — هل أنت جاهز؟"),
    (22.0, 29.0, "B",
     "Bereit. Sende mir die Daten.",
     "Ready. Send me the data.",
     "جاهز. أرسل لي البيانات."),
    (29.0, 38.0, "A",
     "Ich sende Stunden, Verträge und Schichten.",
     "I am sending hours, contracts, and shifts.",
     "أرسل ساعات العمل، والعقود، والمناوبات."),
    (38.0, 44.0, "B",
     "Verstanden.",
     "Understood.",
     "مفهوم."),
    (44.0, 52.0, "B",
     "Ich warte auf den Monatslauf.",
     "I am waiting for the monthly run.",
     "أنتظر تشغيل نهاية الشهر."),
    (52.0, 60.0, "A",
     "Tag achtundzwanzig. Ich öffne die Brücke.",
     "Day twenty-eight. I am opening the bridge.",
     "اليوم الثامن والعشرون. أفتح الجسر."),
    (60.0, 72.0, "B",
     "Die Datenbrücke ist offen. Sicher und verschlüsselt.",
     "The data bridge is open. Secure and encrypted.",
     "جسر البيانات مفتوح. آمن ومشفّر."),
    (72.0, 84.0, "A",
     "Ich komme zu dir mit der Übergabe.",
     "I am coming to you with the handover.",
     "آتي إليك مع تسليم البيانات."),
    (84.0, 96.0, "B",
     "Willkommen in der WorkPass-Lohn Finanzwelt.",
     "Welcome to the WorkPass Lohn financial world.",
     "مرحبًا بك في عالم وورك باس لون المالي."),
    (96.0, 112.0, "B",
     "Ich rechne: Abrechnung, Meldewesen, Kontoauszug und DATEV-Export.",
     "I calculate: payslips, statutory reporting, statements, and DATEV export.",
     "أحسب: كشوف الرواتب، والتقارير الرسمية، وكشف الحساب، وتصدير داتيف."),
    (112.0, 128.0, "A",
     "Die Ergebnisse kehren sicher zur Plattform zurück.",
     "The results return securely to the platform.",
     "تعود النتائج بأمان إلى المنصة."),
    (128.0, 142.0, "B",
     "Goldene Ergebnisse: bereit, compliant und sicher.",
     "Golden results: ready, compliant, and secure.",
     "نتائج ذهبية: جاهزة، ومتوافقة، وآمنة."),
    (142.0, 158.0, "A",
     "Zwei Systeme. Ein Kreislauf. Die Verbindung steht.",
     "Two systems. One cycle. The connection is live.",
     "نظامان. دورة واحدة. الاتصال قائم."),
]

VOICES = {
    "en": {"A": "en-US-GuyNeural", "B": "en-US-JennyNeural"},
    "ar": {"A": "ar-SA-HamedNeural", "B": "ar-SA-ZariyahNeural"},
}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1200:] or r.stdout[-1200:])


def write_wav_mono(path: Path, samples: np.ndarray, sr: int = 24000) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


async def synth_segment(text: str, voice: str, out: Path) -> None:
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save(str(out))


async def build_language(lang: str) -> Path:
    DUB.mkdir(parents=True, exist_ok=True)
    lang_dir = DUB / lang
    lang_dir.mkdir(exist_ok=True)
    sr = 24000
    track = np.zeros(int(DURATION * sr) + sr, dtype=np.float32)

    for i, (start, end, speaker, _de, en, ar) in enumerate(SEGMENTS):
        text = en if lang == "en" else ar
        voice = VOICES[lang][speaker]
        raw = lang_dir / f"seg_{i:02d}.mp3"
        safe = text[:60].encode("ascii", "replace").decode("ascii")
        print(f"[{lang}] {i+1}/{len(SEGMENTS)} {speaker}: {safe}...")
        await synth_segment(text, voice, raw)
        wav = lang_dir / f"seg_{i:02d}.wav"
        run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(sr), str(wav)])
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        slot = max(0.35, end - start)
        max_samples = int(slot * sr)
        if len(audio) > max_samples:
            # slight speed-up via truncate is harsh; prefer ffmpeg atempo
            factor = len(audio) / max_samples
            factor = min(max(factor, 1.01), 1.35)
            sped = lang_dir / f"seg_{i:02d}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_samples]

        # soft fade
        fade = min(int(0.04 * sr), len(audio) // 4)
        if fade > 1:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * sr)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] += audio * 0.95

    # normalize
    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 0.92
    voice_wav = lang_dir / "voice.wav"
    write_wav_mono(voice_wav, track, sr)

    # music bed from original (low) + voice
    music = lang_dir / "music.wav"
    run([FF, "-y", "-i", str(SRC_VIDEO), "-vn", "-ac", "1", "-ar", str(sr),
         "-af", "volume=0.18,highpass=f=120", str(music)])
    mixed = lang_dir / "mixed.wav"
    run([
        FF, "-y",
        "-i", str(music),
        "-i", str(voice_wav),
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0,volume=1.4",
        str(mixed),
    ])

    out_mp4 = ROOT / "assets" / f"workpass-lohn-bridge-{lang}.mp4"
    run([
        FF, "-y",
        "-i", str(SRC_VIDEO),
        "-i", str(mixed),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(out_mp4),
    ])
    print("saved", out_mp4, round(out_mp4.stat().st_size / 1e6, 2), "MB")
    return out_mp4


async def main() -> None:
    scripts = {
        "en": [{"start": s, "end": e, "speaker": sp, "text": en} for s, e, sp, _d, en, _a in SEGMENTS],
        "ar": [{"start": s, "end": e, "speaker": sp, "text": ar} for s, e, sp, _d, _e, ar in SEGMENTS],
    }
    (DUB / "scripts.json").write_text(json.dumps(scripts, ensure_ascii=False, indent=2), encoding="utf-8")
    await build_language("en")
    await build_language("ar")


if __name__ == "__main__":
    asyncio.run(main())
