"""Premium DE VO in narration beats — brand spoken as Suppix Ei-Ai (A-I letters)."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
BEATS_DIR = ROOT / "vo_v7_beats"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = "de-DE-TanjaNeural"
RATE = "-8%"
# Phonetic for neural TTS: English letter names A + I (not German "ai" diphthong)
BRAND = "Suppix Ei-Ai"

# Each beat maps 1:1 to a visual block in build_film_v7_premium.py
BEATS: list[tuple[str, str]] = [
    (
        "01_chaos",
        """Jeden Tag dasselbe Bild.
Zu viele Programme. Doppelte Eingaben.
Excel hier. Chat dort. Stempeluhr woanders.
Die Arbeit wächst – und mit ihr die Last.""",
    ),
    (
        "02_turn",
        f"""Genau hier setzt {BRAND} an.
Ich bin Ihre digitale Begleiterin.
Und ich zeige Ihnen WorkPass – die integrierte Unternehmensplattform.""",
    ),
    (
        "03_platform",
        """WorkPass ist keine weitere App.
Es ist die Plattform, die Vertrag, Identität, Zutritt, Anwesenheit und Betrieb verbindet –
für Unternehmen, Organisationen und Behörden.""",
    ),
    (
        "04_contract",
        """Alles beginnt mit dem Arbeitsvertrag.
Onboarding und digitale Ausweise entstehen in einem Schritt –
ohne manuellen Wildwuchs.""",
    ),
    (
        "05_employee",
        """Dann der Alltag auf dem Gerät des Mitarbeiters:
Zutritt mit QR-Code, NFC oder GPS.
Live. Sicher. Revisionssicher.""",
    ),
    (
        "06_ops",
        """Weniger Systeme. Weniger Tippen. Mehr Kontrolle.
Vom Vertrag bis zum Schichtende: eine Wahrheit.""",
    ),
    (
        "07_tax",
        """Und die Steuer- und Lohnkette bleibt Teil derselben Plattform.
Abrechnung, Meldewesen, DATEV-Export –
verbunden statt zersplittert. Transparent und abschlussbereit.""",
    ),
    (
        "08_engine",
        """Unser Buchhaltungsmotor verarbeitet enorme Datenmengen:
bis zu einhunderttausend Mitarbeitende in nur einhundertfünfzehn Sekunden.""",
    ),
    (
        "09_close",
        f"""Acht Sprachen. White-Label. Enterprise-Sicherheit.
Weniger Aufwand. Weniger manuelle Dateneingabe. Mehr Nähe zu Ihrem Team.
{BRAND}.
Intelligent Work. Connected Future.""",
    ),
]


def probe(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"duration missing: {path}")


async def synth_one(name: str, text: str) -> Path:
    BEATS_DIR.mkdir(parents=True, exist_ok=True)
    out = BEATS_DIR / f"{name}.mp3"
    await edge_tts.Communicate(text.strip(), VOICE, rate=RATE).save(str(out))
    return out


async def main() -> None:
    meta: list[dict] = []
    files: list[Path] = []
    for name, text in BEATS:
        path = await synth_one(name, text)
        dur = probe(path)
        meta.append({"id": name, "file": path.name, "duration": round(dur, 3), "text": text.strip()})
        files.append(path)
        print(f"{name}: {dur:.2f}s")

    # Full concat for reference / easy find
    list_file = BEATS_DIR / "concat.txt"
    list_file.write_text("".join(f"file '{p.name}'\n" for p in files), encoding="utf-8")
    full = ROOT / "vo_v7_premium_full.mp3"
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(full),
        ],
        check=True,
        capture_output=True,
        cwd=str(BEATS_DIR),
    )
    (BEATS_DIR / "beats.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FULL {full} ({probe(full):.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
