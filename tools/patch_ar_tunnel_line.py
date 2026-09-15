"""Patch Arabic tunnel line (~1:02) for clearer platform-robot diction."""
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
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
# Tunnel entry beat (user: after 1:02)
START = 62.0
END = 74.0
# Tashkeel + short beats help Edge neural articulation
TEXT = (
    "وَصَلْتُ. "
    "عَبْرَ النَّفَقِ الْآمِنِ. "
    "أُسَلِّمُ الْحُمُولَةَ لِلتَّحَقُّقِ."
)
VOICE = "ar-SA-HamedNeural"
RATE = "-18%"
PITCH = "-2Hz"


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
    DUB.mkdir(parents=True, exist_ok=True)
    work = DUB / "tunnel-patch"
    work.mkdir(parents=True, exist_ok=True)

    src = ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"
    base_wav = work / "ar-base.wav"
    run([FF, "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", str(SR), str(base_wav)])
    track = read_wav(base_wav)

    raw = work / "tunnel.mp3"
    wav = work / "tunnel.wav"
    print("synth tunnel line")
    await edge_tts.Communicate(TEXT, VOICE, rate=RATE, pitch=PITCH).save(str(raw))
    run([FF, "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), str(wav)])
    audio = read_wav(wav)

    # Soft clarity EQ + slight loudness for this line only
    eq = work / "tunnel-eq.wav"
    run([
        FF, "-y", "-i", str(wav),
        "-af", "highpass=f=90,treble=g=2.5,bass=g=-1,loudnorm=I=-16:TP=-1.5:LRA=8",
        "-ar", str(SR), str(eq),
    ])
    audio = read_wav(eq)

    slot = END - START - 0.35
    max_n = int(slot * SR)
    if len(audio) > max_n:
        factor = min(max(len(audio) / max_n, 1.01), 1.08)
        sped = work / "tunnel-sped.wav"
        run([FF, "-y", "-i", str(eq), "-filter:a", f"atempo={factor:.3f}", str(sped)])
        audio = read_wav(sped)
        audio = audio[:max_n]

    fade = min(int(0.08 * SR), max(1, len(audio) // 12))
    if fade > 1 and len(audio) > fade * 2:
        audio = audio.copy()
        audio[:fade] *= np.linspace(0, 1, fade)
        audio[-fade:] *= np.linspace(1, 0, fade)

    a0 = int(START * SR)
    a1 = int(END * SR)
    # Crossfade edges so replace is seamless
    xfade = int(0.12 * SR)
    replaced = track.copy()
    if len(replaced) < a1:
        replaced = np.pad(replaced, (0, a1 - len(replaced)))

    # Duck old audio in window, then insert new line
    replaced[a0:a1] *= 0.0
    end_pos = a0 + len(audio)
    replaced[a0:end_pos] = audio

    # Tiny edge blend with surrounding track
    if a0 > xfade:
        w = np.linspace(1, 0, xfade)
        replaced[a0 - xfade:a0] = track[a0 - xfade:a0] * w + replaced[a0 - xfade:a0] * (1 - w)
    if end_pos + xfade < len(track):
        w = np.linspace(0, 1, xfade)
        # blend into original after line
        tail = track[end_pos:end_pos + xfade]
        replaced[end_pos:end_pos + xfade] = replaced[end_pos:end_pos + xfade] * (1 - w) + tail * w

    out_wav = work / "ar-patched.wav"
    write_wav(out_wav, replaced)

    out_mp4 = ROOT / "assets" / "workpass-lohn-bridge-ar.mp4"
    tmp = work / "out.mp4"
    run([
        FF, "-y", "-i", str(src), "-i", str(out_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-af", "aformat=channel_layouts=stereo",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart", str(tmp),
    ])
    # Windows may lock the live asset; write via temp then os.replace retry
    import os
    import shutil
    staging = ROOT / "assets" / "workpass-lohn-bridge-ar.new.mp4"
    shutil.copy2(tmp, staging)
    for _ in range(5):
        try:
            os.replace(staging, out_mp4)
            break
        except PermissionError:
            import time
            time.sleep(1.5)
    else:
        raise PermissionError(f"could not replace {out_mp4} (file locked?)")
    print("patched", out_mp4.name, round(out_mp4.stat().st_size / 1e6, 2), "MB")
    print(f"window {START}-{END}s")


if __name__ == "__main__":
    asyncio.run(main())
