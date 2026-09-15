"""Patch Arabic tax line: replace 'حجب' with 'حساب ... حسب' (~1:30)."""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import time
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / "assets" / "lohn-dub"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
START = 76.0
END = 98.0
TEXT = (
    "بعد التحقق من موقع الشركة، والتأكد بنسبة تسعة وتسعين بالمئة من تواجد الموظفين عبر التحديد الجغرافي، "
    "والتأكد من العقود ومواقع العمل ووجود النظام وفي أي دولة يتواجد، "
    "يتم حساب الضرائب حسب الدولة المخصصة بكم والقوانين الخاصة بها."
)
VOICE = "ar-MA-MounaNeural"
RATE = "-8%"
PITCH = "+0Hz"


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-1800:])


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        assert wf.getframerate() == SR
        assert wf.getnchannels() == 1
        return np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


async def main() -> None:
    work = DUB / "tax-patch"
    work.mkdir(parents=True, exist_ok=True)
    src = ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"

    base_wav = work / "ar-base.wav"
    run([FF, "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", str(SR), str(base_wav)])
    track = read_wav(base_wav)

    raw = work / "tax.mp3"
    wav = work / "tax.wav"
    print("synth tax line")
    await edge_tts.Communicate(TEXT, VOICE, rate=RATE, pitch=PITCH).save(str(raw))
    run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), str(wav)])

    eq = work / "tax-eq.wav"
    run([
        FF, "-y", "-i", str(wav),
        "-af", "highpass=f=80,treble=g=1.5,loudnorm=I=-16:TP=-1.5:LRA=9",
        "-ar", str(SR), str(eq),
    ])
    audio = read_wav(eq)

    slot = END - START - 0.3
    max_n = int(slot * SR)
    if len(audio) > max_n:
        factor = min(max(len(audio) / max_n, 1.01), 1.12)
        sped = work / "tax-sped.wav"
        run([FF, "-y", "-i", str(eq), "-filter:a", f"atempo={factor:.3f}", str(sped)])
        audio = read_wav(sped)[:max_n]

    fade = min(int(0.08 * SR), max(1, len(audio) // 12))
    if fade > 1 and len(audio) > fade * 2:
        audio = audio.copy()
        audio[:fade] *= np.linspace(0, 1, fade)
        audio[-fade:] *= np.linspace(1, 0, fade)

    a0 = int(START * SR)
    a1 = int(END * SR)
    replaced = track.copy()
    if len(replaced) < a1:
        replaced = np.pad(replaced, (0, a1 - len(replaced)))
    replaced[a0:a1] = 0.0
    end_pos = a0 + len(audio)
    replaced[a0:end_pos] = audio

    xfade = int(0.12 * SR)
    if a0 > xfade:
        w = np.linspace(1, 0, xfade)
        replaced[a0 - xfade:a0] = track[a0 - xfade:a0] * w + replaced[a0 - xfade:a0] * (1 - w)
    if end_pos + xfade < len(track):
        w = np.linspace(0, 1, xfade)
        replaced[end_pos:end_pos + xfade] = (
            replaced[end_pos:end_pos + xfade] * (1 - w) + track[end_pos:end_pos + xfade] * w
        )

    out_wav = work / "ar-patched.wav"
    write_wav(out_wav, replaced)

    tmp = work / "out.mp4"
    run([
        FF, "-y", "-i", str(src), "-i", str(out_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "aformat=channel_layouts=stereo",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart", str(tmp),
    ])

    out_mp4 = ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"
    staging = ROOT / "assets" / "workpass-lohn-bridge-ar.new.mp4"
    shutil.copy2(tmp, staging)
    for _ in range(6):
        try:
            os.replace(staging, out_mp4)
            break
        except PermissionError:
            time.sleep(1.5)
    else:
        raise PermissionError(f"could not replace {out_mp4}")
    print("patched", out_mp4.name, round(out_mp4.stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    asyncio.run(main())
