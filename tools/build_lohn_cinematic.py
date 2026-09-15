"""
Cinematic Lohn rebuild:
- Full original frame (no stretch/zoom crop) — all content visible
- HQ encode CRF 16 slow from master
- Continuous AR/EN dialogue synced to visual beats (no choppy cuts)
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

# Continuous flowing dialogue synced to scenes (start, end, speaker, text)
# ~30s briefcase opens / data flies → تم التسليم
# ~50s day 28 bridge
# ~100s handshake meeting
SEGMENTS_AR = [
    (0.0, 11.0, "A",
     "النظام متصل. أنا منصة وورك باس، أدير الهوية وأوقات العمل والمواقع في شركتكم بوضوح وأمان."),
    (11.0, 22.0, "B",
     "وأنا المحاسبة. وورك باس لون جاهزة لاستقبال بياناتكم وحساب الرواتب بدقة وفق القانون الألماني."),
    (22.0, 30.0, "A",
     "حسنًا، اسمعي. سأفتح الحقيبة الآمنة وأرسل لك ساعات العمل والعقود والمناوبات الآن."),
    (30.0, 38.0, "B",
     "الحزم وصلت. تم التسليم. استلمت البيانات وهي معزولة وآمنة بين العملاء."),
    (38.0, 50.0, "A",
     "اليوم الثامن والعشرون. أفتح جسر البيانات نحو عالم وورك باس لون المالي."),
    (50.0, 62.0, "B",
     "الجسر مفتوح ومشفّر. تفضّل، ادخُل. سأتحقق من الحمولة فور وصولك."),
    (62.0, 74.0, "A",
     "وصلت عبر النفق الآمن. أسلّم الحمولة للتحقق النهائي."),
    (74.0, 88.0, "B",
     "التحقق اكتمل بنجاح. نبدأ الحساب معًا خطوة بخطوة."),
    (88.0, 102.0, "A",
     "أهلًا بك. بالمصافحة يثبت الاتصال الحي بين المنصة والمحاسبة."),
    (102.0, 118.0, "B",
     "أحسب الآن الرواتب والتقارير وكشف الحساب وتصدير داتيف، ثم أعيد النتائج إليك بأمان."),
    (118.0, 132.0, "A",
     "ممتاز. النتائج عادت إلى المنصة، والموظف يستلم كشفه مباشرة."),
    (132.0, 148.0, "B",
     "نتائج ذهبية: جاهزة ومتوافقة مع القانون وآمنة. من الرواتب حتى صندوق البريد والتطبيقات."),
    (148.0, 158.0, "A",
     "نظامان. دورة واحدة. الاتصال قائم. والعمل مكتمل."),
]

SEGMENTS_EN = [
    (0.0, 11.0, "A",
     "System online. I am the WorkPass platform. I manage identity, working time, and site locations for your company."),
    (11.0, 22.0, "B",
     "And I am accounting. WorkPass Lohn is ready to receive your data and calculate payroll accurately under German law."),
    (22.0, 30.0, "A",
     "Good. I will open the secure case and send you hours, contracts, and shifts now."),
    (30.0, 38.0, "B",
     "Packages received. Delivery complete. The data is isolated and secure across tenants."),
    (38.0, 50.0, "A",
     "Day twenty-eight. I am opening the data bridge into the WorkPass Lohn financial world."),
    (50.0, 62.0, "B",
     "Bridge open and encrypted. Come in. I will verify the payload as soon as you arrive."),
    (62.0, 74.0, "A",
     "I arrived through the secure tunnel. Handing over the payload for final verification."),
    (74.0, 88.0, "B",
     "Verification complete. We start the calculation together, step by step."),
    (88.0, 102.0, "A",
     "Welcome. This handshake confirms the live connection between platform and payroll."),
    (102.0, 118.0, "B",
     "I now calculate payslips, reports, statements, and DATEV export, then return the results securely."),
    (118.0, 132.0, "A",
     "Excellent. Results are back on the platform, and employees receive their payslips directly."),
    (132.0, 148.0, "B",
     "Golden results: ready, compliant, and secure. From payroll to mailbox and apps."),
    (148.0, 158.0, "A",
     "Two systems. One cycle. The connection is live. Work complete."),
]

VOICE_AR = {
    "A": {"voice": "ar-SA-HamedNeural", "rate": "-8%", "pitch": "-4Hz"},
    "B": {"voice": "ar-MA-MounaNeural", "rate": "-6%", "pitch": "+0Hz"},
}
VOICE_EN = {
    "A": {"voice": "en-US-GuyNeural", "rate": "-4%", "pitch": "-2Hz"},
    "B": {"voice": "en-GB-SoniaNeural", "rate": "-2%", "pitch": "+0Hz"},
}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1800:])


def ensure_master() -> Path:
    DUB.mkdir(parents=True, exist_ok=True)
    src = WHATSAPP if WHATSAPP.exists() else MASTER
    if not MASTER.exists() or (WHATSAPP.exists() and WHATSAPP.stat().st_size != MASTER.stat().st_size):
        run([FF, "-y", "-i", str(src), "-c", "copy", str(MASTER)])
    return MASTER


def build_hq_video_fullframe() -> Path:
    """Encode original frame fully — no crop, no stretch, no zoom. Highest practical quality."""
    master = ensure_master()
    out = DUB / "video-hq-full.mp4"
    run([
        FF, "-y", "-i", str(master),
        "-an",
        "-vf", "setsar=1",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "16",
        "-profile:v", "high",
        "-level", "4.1",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out),
    ])
    print("HQ fullframe", round(out.stat().st_size / 1e6, 2), "MB")
    return out


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


async def build_voice(lang: str, segments, voices) -> Path:
    lang_dir = DUB / f"{lang}-cine"
    lang_dir.mkdir(parents=True, exist_ok=True)
    track = np.zeros(int(DURATION * SR) + SR, dtype=np.float32)

    for i, (start, end, speaker, text) in enumerate(segments):
        cfg = voices[speaker]
        raw = lang_dir / f"seg_{i:02d}_{speaker}.mp3"
        wav = lang_dir / f"seg_{i:02d}_{speaker}.wav"
        print(f"[{lang} {i+1}/{len(segments)}] {speaker} {start}-{end}")
        await edge_tts.Communicate(
            text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"]
        ).save(str(raw))
        run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), str(wav)])
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        # Prefer natural pace: only tiny speed-up if needed, never choppy
        slot = max(0.8, end - start - 0.35)
        max_n = int(slot * SR)
        if len(audio) > max_n:
            factor = min(max(len(audio) / max_n, 1.01), 1.12)
            sped = lang_dir / f"seg_{i:02d}_{speaker}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            if len(audio) > max_n:
                audio = audio[:max_n]

        # Soft crossfade edges for continuous feel
        fade = min(int(0.08 * SR), max(1, len(audio) // 8))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        # Soft duck if overlapping previous tail
        track[pos:end_pos] = track[pos:end_pos] * 0.15 + audio * 0.95

    peak = np.max(np.abs(track)) or 1.0
    voice = lang_dir / "voice.wav"
    write_wav(voice, track / peak * 0.9)
    voice_n = lang_dir / "voice-ln.wav"
    run([
        FF, "-y", "-i", str(voice),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=70",
        "-ar", str(SR),
        str(voice_n),
    ])
    return voice_n


def mux_voice(video: Path, audio: Path, out: Path) -> None:
    run([
        FF, "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "aformat=channel_layouts=stereo",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart",
        str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


def mux_de(video: Path, master: Path, out: Path) -> None:
    run([
        FF, "-y", "-i", str(video), "-i", str(master),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart",
        str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


async def main() -> None:
    video = build_hq_video_fullframe()
    master = ensure_master()
    mux_de(video, master, ROOT / "assets" / "workpass-lohn-bridge-de.mp4")
    en = await build_voice("en", SEGMENTS_EN, VOICE_EN)
    mux_voice(video, en, ROOT / "assets" / "workpass-lohn-bridge-en.mp4")
    ar = await build_voice("ar", SEGMENTS_AR, VOICE_AR)
    mux_voice(video, ar, ROOT / "assets" / "workpass-lohn-bridge-ar.mp4")
    run([
        FF, "-y", "-ss", "100",
        "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "2",
        str(ROOT / "assets" / "workpass-lohn-bridge-poster.jpg"),
    ])
    print("poster ok")


if __name__ == "__main__":
    asyncio.run(main())
