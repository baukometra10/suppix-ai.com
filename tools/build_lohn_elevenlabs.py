"""
Mux Lohn videos from ElevenLabs MP3 drops (preferred) or Edge-TTS fallback.

Drop files into:
  assets/lohn-dub/elevenlabs/ar/*.mp3
  assets/lohn-dub/elevenlabs/en/*.mp3

Optional: set ELEVENLABS_API_KEY / XI_API_KEY to synthesize via API
using voice IDs in VOICE_IDS below (fill with your cloned voices).

Usage:
  python tools/build_lohn_elevenlabs.py
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / "assets" / "lohn-dub"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
DURATION = 161.5

# Fill with your ElevenLabs voice IDs when cloning Mazen / Mo Wiseman etc.
VOICE_IDS = {
    "ar": {"A": "", "B": ""},
    "en": {"A": "", "B": ""},
}

SEGMENTS_AR = [
    (0.0, 12.0, "A", "النظام متصل. أنا منصة وورك باس. أدير الهوية وأوقات العمل والمواقع في شركتكم بوضوح."),
    (12.0, 24.0, "B", "وأنا نظام المحاسبة وورك باس لون. جاهزة لاستقبال بياناتكم وحساب الرواتب بدقة."),
    (24.0, 32.0, "A", "حسنًا. سأفتح الحقيبة الآمنة وأرسل لك ساعات العمل والعقود والمناوبات الآن."),
    (32.0, 40.0, "B", "الحزم وصلت. تم التسليم. البيانات معزولة وآمنة."),
    (40.0, 52.0, "A", "اليوم الثامن والعشرون. أفتح جسر البيانات نحو عالم المحاسبة المالي."),
    (52.0, 64.0, "B", "الجسر مفتوح ومشفّر. تفضّل، ادخُل. سأبدأ التحقق فور وصولك."),
    (62.0, 74.0, "A", "وَصَلْتُ. عَبْرَ النَّفَقِ الْآمِنِ. أُسَلِّمُ الْحُمُولَةَ لِلتَّحَقُّقِ."),
    (76.0, 98.0, "B",
     "بعد التحقق من موقع الشركة، والتأكد بنسبة تسعة وتسعين بالمئة من تواجد الموظفين عبر التحديد الجغرافي، "
     "والتأكد من العقود ومواقع العمل ووجود النظام وفي أي دولة يتواجد، "
     "يتم حساب الضرائب حسب الدولة المخصصة بكم والقوانين الخاصة بها."),
    (98.0, 110.0, "A", "أهلًا بك. بالمصافحة يثبت الاتصال الحي بين المنصة ونظام وورك باس لون."),
    (110.0, 124.0, "B", "أحسب الآن الرواتب والتقارير وكشف الحساب وتصدير داتيف، ثم أعيد النتائج إليك بأمان."),
    (124.0, 138.0, "A", "ممتاز. النتائج عادت إلى المنصة، والموظف يستلم كشفه مباشرة."),
    (138.0, 150.0, "B", "نتائج ذهبية: جاهزة ومتوافقة وآمنة. من الرواتب حتى صندوق البريد والتطبيقات."),
    (150.0, 159.0, "A", "نظامان. دورة واحدة. وداعًا إلى الشهر المقبل."),
    (152.5, 159.5, "B", "إلى الشهر المقبل."),
]

SEGMENTS_EN = [
    (0.0, 12.0, "A", "System online. I am the WorkPass platform. I manage identity, working time, and site locations for your company."),
    (12.0, 24.0, "B", "And I am the WorkPass Lohn accounting system. Ready to receive your data and calculate payroll accurately."),
    (24.0, 32.0, "A", "Good. I will open the secure case and send you hours, contracts, and shifts now."),
    (32.0, 40.0, "B", "Packages received. Delivery complete. The data is isolated and secure."),
    (40.0, 52.0, "A", "Day twenty-eight. I am opening the data bridge into the financial world."),
    (52.0, 64.0, "B", "Bridge open and encrypted. Come in. I will start verification as soon as you arrive."),
    (64.0, 76.0, "A", "I arrived through the secure tunnel. Handing over the payload for verification."),
    (76.0, 98.0, "B",
     "After verifying the company location, confirming employee presence at about ninety-nine percent via geofencing, "
     "and checking contracts, work sites, and where the system is hosted, "
     "taxes are calculated according to your designated country and its laws."),
    (98.0, 110.0, "A", "Welcome. This handshake confirms the live connection between the platform and WorkPass Lohn."),
    (110.0, 124.0, "B", "I now calculate payslips, reports, statements, and DATEV export, then return the results securely."),
    (124.0, 138.0, "A", "Excellent. Results are back on the platform, and employees receive their payslips directly."),
    (138.0, 150.0, "B", "Golden results: ready, compliant, and secure. From payroll to mailbox and apps."),
    (150.0, 159.0, "A", "Two systems. One cycle. Goodbye until next month."),
    (152.5, 159.5, "B", "Until next month."),
]

EDGE = {
    "ar": {
        "A": {"voice": "ar-SA-HamedNeural", "rate": "-14%", "pitch": "-3Hz"},
        "B": {"voice": "ar-MA-MounaNeural", "rate": "-10%", "pitch": "+0Hz"},
    },
    "en": {
        "A": {"voice": "en-US-GuyNeural", "rate": "-6%", "pitch": "-2Hz"},
        "B": {"voice": "en-GB-SoniaNeural", "rate": "-4%", "pitch": "+0Hz"},
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


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        return np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def api_key() -> str:
    return (os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("XI_API_KEY") or "").strip()


def synth_eleven_api(text: str, voice_id: str, out_mp3: Path) -> bool:
    key = api_key()
    if not key or not voice_id:
        return False
    import urllib.request
    import json

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        out_mp3.write_bytes(resp.read())
    return out_mp3.exists() and out_mp3.stat().st_size > 500


async def build_track(lang: str, segments) -> Path:
    work = DUB / f"{lang}-eleven"
    work.mkdir(parents=True, exist_ok=True)
    drop = DUB / "elevenlabs" / lang
    track = np.zeros(int(DURATION * SR) + SR, dtype=np.float32)
    used_api = 0
    used_drop = 0
    used_edge = 0

    for i, (start, end, speaker, text) in enumerate(segments):
        stem = f"seg_{i:02d}_{speaker}"
        drop_mp3 = drop / f"{stem}.mp3"
        # also accept script naming ar_A_00.mp3 style loosely
        alt = list(drop.glob(f"*{speaker}_{i:02d}*.mp3")) if drop.exists() else []
        raw = work / f"{stem}.mp3"
        wav = work / f"{stem}.wav"

        if drop_mp3.exists():
            raw.write_bytes(drop_mp3.read_bytes())
            used_drop += 1
        elif alt:
            raw.write_bytes(alt[0].read_bytes())
            used_drop += 1
        elif synth_eleven_api(text, VOICE_IDS.get(lang, {}).get(speaker, ""), raw):
            used_api += 1
        else:
            cfg = EDGE[lang][speaker]
            await edge_tts.Communicate(
                text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"]
            ).save(str(raw))
            used_edge += 1

        run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), str(wav)])
        audio = read_wav(wav)
        slot = max(0.9, end - start - 0.25)
        max_n = int(slot * SR)
        if len(audio) > max_n:
            factor = min(max(len(audio) / max_n, 1.01), 1.12)
            sped = work / f"{stem}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            audio = read_wav(sped)[:max_n]
        fade = min(int(0.08 * SR), max(1, len(audio) // 12))
        if fade > 1 and len(audio) > fade * 2:
            audio = audio.copy()
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)
        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] = track[pos:end_pos] * 0.1 + audio * 0.95

    peak = np.max(np.abs(track)) or 1.0
    voice = work / "voice.wav"
    write_wav(voice, track / peak * 0.9)
    voice_n = work / "voice-ln.wav"
    run([
        FF, "-y", "-i", str(voice),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=80,treble=g=1.2",
        "-ar", str(SR), str(voice_n),
    ])
    print(f"[{lang}] drop={used_drop} api={used_api} edge={used_edge}")
    return voice_n


def mux(video: Path, audio: Path, out: Path) -> None:
    run([
        FF, "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "aformat=channel_layouts=stereo",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart", str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


async def main() -> None:
    video = ROOT / "assets" / "workpass-lohn-bridge-de.mp4"
    if not video.exists():
        raise SystemExit("missing DE video master visual track")
    # reuse current DE video as silent-capable visual (has DE audio; we remap)
    ar = await build_track("ar", SEGMENTS_AR)
    mux(video, ar, ROOT / "assets" / "workpass-lohn-bridge-ar.mp4")
    en = await build_track("en", SEGMENTS_EN)
    mux(video, en, ROOT / "assets" / "workpass-lohn-bridge-en.mp4")
    print("done — drop ElevenLabs MP3s or set ELEVENLABS_API_KEY for full clone quality")


if __name__ == "__main__":
    asyncio.run(main())
