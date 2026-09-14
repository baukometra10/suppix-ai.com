"""Transcribe WorkPass Lohn DE audio with Whisper."""
import json
import os
import shutil
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import whisper

ROOT = Path(__file__).resolve().parents[1]
WAV = ROOT / "assets" / "lohn-dub" / "de-audio.wav"
OUT_JSON = ROOT / "assets" / "lohn-dub" / "transcript-de.json"
OUT_TXT = ROOT / "assets" / "lohn-dub" / "transcript-de.txt"


def ensure_ffmpeg_on_path() -> None:
    ff = Path(imageio_ffmpeg.get_ffmpeg_exe())
    shim_dir = ROOT / "tools" / ".ffmpeg-shim"
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim = shim_dir / "ffmpeg.exe"
    if not shim.exists() or shim.stat().st_size != ff.stat().st_size:
        shutil.copyfile(ff, shim)
    os.environ["PATH"] = str(shim_dir) + os.pathsep + os.environ.get("PATH", "")


def load_wav_mono_f32(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 16000
        raw = wf.readframes(wf.getnframes())
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return audio


def main() -> None:
    ensure_ffmpeg_on_path()
    print("ffmpeg shim ready:", shutil.which("ffmpeg"))
    print("loading model...")
    model = whisper.load_model("base")
    print("loading wav...")
    audio = load_wav_mono_f32(WAV)
    print("transcribing...", audio.shape)
    result = model.transcribe(audio, language="de", verbose=False)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = []
    for s in result.get("segments", []):
        lines.append(f"{s['start']:.1f}-{s['end']:.1f}: {s['text'].strip()}")
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print("segments", len(result.get("segments", [])))
    print(result.get("text", "")[:2500])


if __name__ == "__main__":
    main()
