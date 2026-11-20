"""Build film VO: real Marlena preview lead-in + extended professional German body.

Brand spoken as „Suppix AI“. Includes closing tax/payroll beat for end showcase.
"""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
MARLENA = ROOT / "marlena_preview.mp3"
BODY = ROOT / "vo_body_extended.mp3"
OUT = ROOT / "vo_film_marlena_extended.mp3"
VOICE = "de-DE-TanjaNeural"

# Body continues after Marlena's short greeting; tax beat last so visuals can follow.
SCRIPT = """
Ich bin Ihre digitale Begleiterin von Suppix AI.
Heute zeige ich Ihnen WorkPass – unsere integrierte Unternehmensplattform.

WorkPass ist keine einzelne App.
Es ist eine vollständige Plattform für Unternehmen, Organisationen und Behörden:
für Bau, Industrie, Pflege, Logistik und den öffentlichen Sektor.

Alles beginnt mit dem Arbeitsvertrag.
Identität, Onboarding und digitale Ausweise entstehen in einem Schritt.

Dann folgt der Alltag auf dem Gerät des Mitarbeiters:
Zutritt mit QR-Code, NFC oder GPS, Live-Anwesenheit und Schichten –
sicher, revisionssicher und mandantenfähig.

Am Ende des Monats bleibt alles verbunden.
Arbeitszeiten fließen in die Lohnkette – bis zur klaren Gehaltsabrechnung.
Vom Arbeitsvertrag bis zur Gehaltsabrechnung:
eine Plattform, ein Prozess, eine Wahrheit.

Acht Sprachen. White-Label. Enterprise-Sicherheit.
Weniger Systembrüche. Mehr Kontrolle. Mehr Nähe zu Ihrem Team.

Und die Steuerkette bleibt Teil derselben Plattform:
Lohn, Abgaben und Abrechnung – transparent, verbunden und bereit für Ihren Abschluss.

Suppix AI.
Intelligent Work. Connected Future.
"""


async def synth_body() -> None:
    communicate = edge_tts.Communicate(SCRIPT.strip(), VOICE, rate="-10%")
    await communicate.save(str(BODY))
    print(f"saved {BODY}")


def concat_marlena_then_body() -> None:
    # Normalize both to same format, slight crossfade feel via short silence gap.
    marlena_wav = ROOT / "_marlena_norm.wav"
    body_wav = ROOT / "_body_norm.wav"
    gap_wav = ROOT / "_gap.wav"
    for src, dst, af in (
        (MARLENA, marlena_wav, "loudnorm=I=-16:TP=-1.5:LRA=11"),
        (BODY, body_wav, "loudnorm=I=-16:TP=-1.5:LRA=11"),
    ):
        subprocess.run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(src),
                "-af",
                af,
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dst),
            ],
            check=True,
            capture_output=True,
        )
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=mono",
            "-t",
            "0.35",
            str(gap_wav),
        ],
        check=True,
        capture_output=True,
    )
    list_file = ROOT / "_vo_concat.txt"
    list_file.write_text(
        f"file '{marlena_wav.name}'\nfile '{gap_wav.name}'\nfile '{body_wav.name}'\n",
        encoding="utf-8",
    )
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
            str(OUT),
        ],
        check=True,
        capture_output=True,
        cwd=str(ROOT),
    )
    for p in (marlena_wav, body_wav, gap_wav, list_file, BODY):
        if p.exists():
            p.unlink()
    print(f"saved {OUT}")


async def main() -> None:
    if not MARLENA.exists():
        raise SystemExit(f"missing {MARLENA}")
    await synth_body()
    concat_marlena_then_body()


if __name__ == "__main__":
    asyncio.run(main())
