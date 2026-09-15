"""
Lohn cinematic v2:
- Remove early letterbox via blur-fill (no stretch / no side-crop zoom)
- Continuous AR/EN dialogue: correct WorkPass Lohn name, country-based tax,
  verification (geo/contracts/sites), goodbye until next month
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
TOP = 246  # measured letterbox on early scenes

# Phonetic-friendly name for Arabic TTS
NAME_AR = "وورك باس لون"
NAME_EN = "WorkPass Lohn"

SEGMENTS_AR = [
    (0.0, 12.0, "A",
     f"النظام متصل. أنا منصة وورك باس. أدير الهوية وأوقات العمل والمواقع في شركتكم بوضوح."),
    (12.0, 24.0, "B",
     f"وأنا نظام المحاسبة {NAME_AR}. جاهزة لاستقبال بياناتكم وحساب الرواتب بدقة."),
    (24.0, 32.0, "A",
     "حسنًا. سأفتح الحقيبة الآمنة وأرسل لك ساعات العمل والعقود والمناوبات الآن."),
    (32.0, 40.0, "B",
     "الحزم وصلت. تم التسليم. البيانات معزولة وآمنة."),
    (40.0, 52.0, "A",
     "اليوم الثامن والعشرون. أفتح جسر البيانات نحو عالم المحاسبة المالي."),
    (52.0, 64.0, "B",
     "الجسر مفتوح ومشفّر. تفضّل، ادخُل. سأبدأ التحقق فور وصولك."),
    (62.0, 74.0, "A",
     "وَصَلْتُ. عَبْرَ النَّفَقِ الْآمِنِ. أُسَلِّمُ الْحُمُولَةَ لِلتَّحَقُّقِ."),
    (76.0, 98.0, "B",
     "بعد التحقق من موقع الشركة، والتأكد بنسبة تسعة وتسعين بالمئة من تواجد الموظفين عبر التحديد الجغرافي، "
     "والتأكد من العقود ومواقع العمل ووجود النظام وفي أي دولة يتواجد، "
     "يتم حجب الضرائب وفق الدولة المخصصة بكم والقوانين الخاصة بها."),
    (98.0, 110.0, "A",
     f"أهلًا بك. بالمصافحة يثبت الاتصال الحي بين المنصة ونظام {NAME_AR}."),
    (110.0, 124.0, "B",
     "أحسب الآن الرواتب والتقارير وكشف الحساب وتصدير داتيف، ثم أعيد النتائج إليك بأمان."),
    (124.0, 138.0, "A",
     "ممتاز. النتائج عادت إلى المنصة، والموظف يستلم كشفه مباشرة."),
    (138.0, 150.0, "B",
     "نتائج ذهبية: جاهزة ومتوافقة وآمنة. من الرواتب حتى صندوق البريد والتطبيقات."),
    (150.0, 159.0, "A",
     "نظامان. دورة واحدة. وداعًا إلى الشهر المقبل."),
    (152.5, 159.5, "B",
     "إلى الشهر المقبل."),
]

SEGMENTS_EN = [
    (0.0, 12.0, "A",
     "System online. I am the WorkPass platform. I manage identity, working time, and site locations for your company."),
    (12.0, 24.0, "B",
     f"And I am the {NAME_EN} accounting system. Ready to receive your data and calculate payroll accurately."),
    (24.0, 32.0, "A",
     "Good. I will open the secure case and send you hours, contracts, and shifts now."),
    (32.0, 40.0, "B",
     "Packages received. Delivery complete. The data is isolated and secure."),
    (40.0, 52.0, "A",
     "Day twenty-eight. I am opening the data bridge into the financial world."),
    (52.0, 64.0, "B",
     "Bridge open and encrypted. Come in. I will start verification as soon as you arrive."),
    (64.0, 76.0, "A",
     "I arrived through the secure tunnel. Handing over the payload for verification."),
    (76.0, 98.0, "B",
     "After verifying the company location, confirming employee presence at about ninety-nine percent via geofencing, "
     "and checking contracts, work sites, and where the system is hosted, "
     "taxes are withheld according to your designated country and its laws."),
    (98.0, 110.0, "A",
     f"Welcome. This handshake confirms the live connection between the platform and {NAME_EN}."),
    (110.0, 124.0, "B",
     "I now calculate payslips, reports, statements, and DATEV export, then return the results securely."),
    (124.0, 138.0, "A",
     "Excellent. Results are back on the platform, and employees receive their payslips directly."),
    (138.0, 150.0, "B",
     "Golden results: ready, compliant, and secure. From payroll to mailbox and apps."),
    (150.0, 159.0, "A",
     "Two systems. One cycle. Goodbye until next month."),
    (152.5, 159.5, "B",
     "Until next month."),
]

VOICE_AR = {
    "A": {"voice": "ar-SA-HamedNeural", "rate": "-6%", "pitch": "-4Hz"},
    "B": {"voice": "ar-MA-MounaNeural", "rate": "-4%", "pitch": "+0Hz"},
}
VOICE_EN = {
    "A": {"voice": "en-US-GuyNeural", "rate": "-2%", "pitch": "-2Hz"},
    "B": {"voice": "en-GB-SoniaNeural", "rate": "+0%", "pitch": "+0Hz"},
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


def build_hq_video() -> Path:
    """Crop authored letterbox; mild height fit + bright blur fill (no side crop)."""
    master = ensure_master()
    out = DUB / "video-hq-v2.mp4"
    part1 = DUB / "hq-part1.mp4"
    part2 = DUB / "hq-part2.mp4"

    def encode(out_path: Path, top: int, duration: float | None, ss: float | None) -> None:
        ch = 720 - top
        ch -= ch % 2
        fg_h = 640
        fc = (
            f"[0:v]crop=1280:{ch}:0:{top},split=2[fg][bg];"
            f"[bg]scale=1280:720,gblur=sigma=28,"
            f"eq=brightness=0.14:saturation=1.15:contrast=1.05[bg2];"
            f"[fg]scale=1280:{fg_h}[fg2];"
            f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1"
        )
        cmd = [FF, "-y"]
        if ss is not None:
            cmd += ["-ss", str(ss)]
        cmd += ["-i", str(master)]
        if duration is not None:
            cmd += ["-t", str(duration)]
        cmd += [
            "-filter_complex", fc, "-an",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16",
            "-profile:v", "high", "-pix_fmt", "yuv420p", str(out_path),
        ]
        run(cmd)

    encode(part1, top=TOP, duration=SPLIT, ss=None)
    encode(part2, top=40, duration=None, ss=SPLIT)
    lst = DUB / "hq-concat.txt"
    lst.write_text(
        f"file '{part1.resolve().as_posix()}'\nfile '{part2.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    print("HQ video (blur-fill)", round(out.stat().st_size / 1e6, 2), "MB")
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
    lang_dir = DUB / f"{lang}-v2"
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

        slot = max(0.9, end - start - 0.25)
        max_n = int(slot * SR)
        if len(audio) > max_n:
            factor = min(max(len(audio) / max_n, 1.01), 1.10)
            sped = lang_dir / f"seg_{i:02d}_{speaker}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_n]

        fade = min(int(0.1 * SR), max(1, len(audio) // 10))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * SR)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] = track[pos:end_pos] * 0.12 + audio * 0.95

    peak = np.max(np.abs(track)) or 1.0
    voice = lang_dir / "voice.wav"
    write_wav(voice, track / peak * 0.9)
    voice_n = lang_dir / "voice-ln.wav"
    run([
        FF, "-y", "-i", str(voice),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=70",
        "-ar", str(SR), str(voice_n),
    ])
    return voice_n


def mux_voice(video: Path, audio: Path, out: Path) -> None:
    run([
        FF, "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "aformat=channel_layouts=stereo",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart", str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


def mux_de(video: Path, master: Path, out: Path) -> None:
    run([
        FF, "-y", "-i", str(video), "-i", str(master),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart", str(out),
    ])
    print("saved", out.name, round(out.stat().st_size / 1e6, 2), "MB")


async def main() -> None:
    video = build_hq_video()
    master = ensure_master()
    mux_de(video, master, ROOT / "assets" / "workpass-lohn-bridge-de.mp4")
    en = await build_voice("en", SEGMENTS_EN, VOICE_EN)
    mux_voice(video, en, ROOT / "assets" / "workpass-lohn-bridge-en.mp4")
    ar = await build_voice("ar", SEGMENTS_AR, VOICE_AR)
    mux_voice(video, ar, ROOT / "assets" / "workpass-lohn-bridge-ar.mp4")
    run([
        FF, "-y", "-ss", "9",
        "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "2",
        str(ROOT / "assets" / "workpass-lohn-bridge-poster.jpg"),
    ])
    # verify letterbox gone at t=9
    shot = DUB / "_check9.jpg"
    run([
        FF, "-y", "-ss", "9", "-i", str(ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"),
        "-frames:v", "1", "-update", "1", "-q:v", "3", str(shot),
    ])
    from PIL import Image
    g = np.array(Image.open(shot).convert("RGB")).mean(axis=2)
    top = next((y for y in range(g.shape[0]) if g[y].mean() > 12), 0)
    print("t9 topbar", top)
    print("poster ok")


if __name__ == "__main__":
    asyncio.run(main())
