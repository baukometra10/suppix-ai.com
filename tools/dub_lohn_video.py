"""
Rebuild AR/EN WorkPass Lohn videos:
- no German speech bleed (voice-only + optional soft bed)
- clearer Arabic with tashkeel + slower neural voices
- remove early-scene top letterbox via split crop/zoom + concat
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
MASTER = DUB / "master-de-src.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
DURATION = 161.5
SPLIT_AT = 92.0  # early letterboxed scenes end around here
TOP_CROP = 246

# Clear Arabic with diacritics for better articulation
SEGMENTS = [
    (0.0, 6.5, "A",
     "System online. I am the platform.",
     "النِّظَامُ مُتَّصِل. أَنَا المِنَصَّة."),
    (6.5, 14.0, "B",
     "I am WorkPass Lohn.",
     "أَنَا وُورْك بَاس لُون لِلْمُحَاسَبَة."),
    (14.0, 18.0, "B",
     "I hear you.",
     "أَسْمَعُك بِوُضُوح."),
    (18.0, 23.0, "A",
     "WorkPass Lohn — are you ready?",
     "وُورْك بَاس لُون، هَلْ أَنْتَ جَاهِز؟"),
    (23.0, 29.0, "B",
     "Ready. Send me the data.",
     "جَاهِز. أَرْسِلْ إِلَيَّ البَيَانَات."),
    (29.0, 38.0, "A",
     "I am sending hours, contracts, and shifts.",
     "أُرْسِلُ سَاعَاتِ العَمَل، وَالعُقُود، وَالمُنَاوَبَات."),
    (38.0, 44.0, "B",
     "Understood.",
     "مَفْهُوم. تَمَّ الاِسْتِلَام."),
    (44.0, 52.0, "B",
     "I am waiting for the monthly run.",
     "أَنْتَظِرُ تَشْغِيلَ نِهَايَةِ الشَّهْر."),
    (52.0, 60.0, "A",
     "Day twenty-eight. I am opening the bridge.",
     "اليَوْمُ الثَّامِنُ وَالعِشْرُون. أَفْتَحُ الجِسْر."),
    (60.0, 72.0, "B",
     "The data bridge is open. Secure and encrypted.",
     "جِسْرُ البَيَانَاتِ مَفْتُوح. آمِنٌ وَمُشَفَّر."),
    (72.0, 84.0, "A",
     "I am coming to you with the handover.",
     "آتِي إِلَيْكَ مَعَ تَسْلِيمِ البَيَانَات."),
    (84.0, 96.0, "B",
     "Welcome to the WorkPass Lohn financial world.",
     "مَرْحَبًا بِكَ فِي عَالَمِ وُورْك بَاس لُون المَالِي."),
    (96.0, 112.0, "B",
     "I calculate payslips, statutory reporting, statements, and DATEV export.",
     "أَحْسِبُ كُشُوفَ الرَّوَاتِب، وَالتَّقَارِيرَ الرَّسْمِيَّة، وَكَشْفَ الحِسَاب، وَتَصْدِيرَ دَاتِيف."),
    (112.0, 128.0, "A",
     "The results return securely to the platform.",
     "تَعُودُ النَّتَائِجُ بِأَمَانٍ إِلَى المِنَصَّة."),
    (128.0, 142.0, "B",
     "Golden results: ready, compliant, and secure.",
     "نَتَائِجُ ذَهَبِيَّة: جَاهِزَة، وَمُتَوَافِقَة، وَآمِنَة."),
    (142.0, 158.0, "A",
     "Two systems. One cycle. The connection is live.",
     "نِظَامَان. دَوْرَةٌ وَاحِدَة. الاِتِّصَالُ قَائِم."),
]

VOICES = {
    "en": {"A": "en-US-GuyNeural", "B": "en-GB-SoniaNeural"},
    "ar": {"A": "ar-SA-HamedNeural", "B": "ar-EG-SalmaNeural"},
}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1500:])


def write_wav_mono(path: Path, samples: np.ndarray, sr: int = 24000) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


async def synth_segment(text: str, voice: str, out: Path, lang: str) -> None:
    rate = "-18%" if lang == "ar" else "-8%"
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(out))


def ensure_master() -> Path:
    """Keep one untouched DE source so we never overwrite the audio master."""
    DUB.mkdir(parents=True, exist_ok=True)
    whatsapp = Path(
        r"c:\Users\u4363\Desktop\Screenshots\WhatsApp Video 2026-09-02 at 15 (online-video-cutter.com) (1).mp4"
    )
    src = whatsapp if whatsapp.exists() else SRC_VIDEO
    if not MASTER.exists() or MASTER.stat().st_size < 1_000_000:
        run([FF, "-y", "-i", str(src), "-c", "copy", str(MASTER)])
        print("master saved from", src.name)
    return MASTER


def build_clean_video() -> Path:
    """Remove early top letterbox by zoom-filling first part, keep rest, concat."""
    master = ensure_master()
    part1 = DUB / "video-part1.mp4"
    part2 = DUB / "video-part2.mp4"
    cleaned = DUB / "video-clean.mp4"
    content_h = 720 - TOP_CROP
    content_h -= content_h % 2
    # Zoom early letterboxed scenes to fill frame (no black bar)
    vf1 = (
        f"crop=1280:{content_h}:0:{TOP_CROP},"
        f"scale=1280:720:force_original_aspect_ratio=increase,"
        f"crop=1280:720,setsar=1"
    )
    run([
        FF, "-y", "-i", str(master),
        "-t", str(SPLIT_AT),
        "-vf", vf1,
        "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        str(part1),
    ])
    # Later scenes: mild top trim
    vf2 = "crop=1280:680:0:40,scale=1280:720,setsar=1"
    run([
        FF, "-y", "-ss", str(SPLIT_AT), "-i", str(master),
        "-vf", vf2,
        "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        str(part2),
    ])
    lst = DUB / "concat.txt"
    lst.write_text(
        f"file '{part1.resolve().as_posix()}'\nfile '{part2.resolve().as_posix()}'\n",
        encoding="utf-8",
    )
    run([
        FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy",
        str(cleaned),
    ])
    print("clean video", cleaned)
    return cleaned


async def build_language(lang: str, clean_video: Path) -> Path:
    lang_dir = DUB / lang
    lang_dir.mkdir(exist_ok=True)
    sr = 24000
    track = np.zeros(int(DURATION * sr) + sr, dtype=np.float32)

    for i, (start, end, speaker, en, ar) in enumerate(SEGMENTS):
        text = en if lang == "en" else ar
        voice = VOICES[lang][speaker]
        raw = lang_dir / f"seg_{i:02d}.mp3"
        safe = text[:50].encode("ascii", "replace").decode("ascii")
        print(f"[{lang}] {i+1}/{len(SEGMENTS)} {speaker}: {safe}")
        await synth_segment(text, voice, raw, lang)
        wav = lang_dir / f"seg_{i:02d}.wav"
        run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(sr), str(wav)])
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        slot = max(0.4, end - start - 0.15)
        max_samples = int(slot * sr)
        if len(audio) > max_samples:
            factor = min(max(len(audio) / max_samples, 1.01), 1.28)
            sped = lang_dir / f"seg_{i:02d}_sped.wav"
            run([FF, "-y", "-i", str(wav), "-filter:a", f"atempo={factor:.3f}", str(sped)])
            with wave.open(str(sped), "rb") as wf:
                audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            audio = audio[:max_samples]

        fade = min(int(0.05 * sr), max(1, len(audio) // 5))
        if fade > 1 and len(audio) > fade * 2:
            audio[:fade] *= np.linspace(0, 1, fade)
            audio[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start * sr)
        end_pos = pos + len(audio)
        if end_pos > len(track):
            track = np.pad(track, (0, end_pos - len(track)))
        track[pos:end_pos] += audio * 0.98

    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 0.95
    voice_wav = lang_dir / "voice-only.wav"
    write_wav_mono(voice_wav, track, sr)

    # Soft non-speech bed: low-pass noise from original with vocals crushed,
    # then duck heavily — still may leak. Safer: silence + very quiet tone bed.
    # Use NO original audio at all.
    out_mp4 = ROOT / "assets" / f"workpass-lohn-bridge-{lang}.mp4"
    run([
        FF, "-y",
        "-i", str(clean_video),
        "-i", str(voice_wav),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(out_mp4),
    ])
    print("saved", out_mp4.name, round(out_mp4.stat().st_size / 1e6, 2), "MB")
    return out_mp4


async def main() -> None:
    scripts = {
        "en": [{"start": s, "end": e, "speaker": sp, "text": en} for s, e, sp, en, _ar in SEGMENTS],
        "ar": [{"start": s, "end": e, "speaker": sp, "text": ar} for s, e, sp, _en, ar in SEGMENTS],
    }
    (DUB / "scripts-v2.json").write_text(json.dumps(scripts, ensure_ascii=False, indent=2), encoding="utf-8")
    master = ensure_master()
    clean = build_clean_video()
    de_out = ROOT / "assets" / "workpass-lohn-bridge-de.mp4"
    run([
        FF, "-y",
        "-i", str(clean),
        "-i", str(master),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(de_out),
    ])
    print("refreshed DE visual", de_out.name)
    await build_language("en", clean)
    await build_language("ar", clean)


if __name__ == "__main__":
    asyncio.run(main())
