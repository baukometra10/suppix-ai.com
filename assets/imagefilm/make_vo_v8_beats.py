"""Premium DE VO v8 — natural pace; brand „Suppix AI“ spoken with English neural voice."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
BEATS_DIR = ROOT / "vo_v8_beats"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE_DE = "de-DE-TanjaNeural"
VOICE_EN = "en-US-JennyNeural"
RATE_DE = "-6%"
RATE_EN = "-2%"


def probe(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(path)


def concat_mp3(parts: list[Path], out: Path) -> None:
    lst = out.with_suffix(".txt")
    # Normalize each to wav then concat for reliable joins
    wavs = []
    for i, p in enumerate(parts):
        w = out.parent / f"_part_{out.stem}_{i}.wav"
        subprocess.run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(p),
                "-ar",
                "44100",
                "-ac",
                "1",
                "-af",
                "loudnorm=I=-16:TP=-1.5:LRA=11",
                str(w),
            ],
            check=True,
            capture_output=True,
        )
        wavs.append(w)
    lst.write_text("".join(f"file '{w.name}'\n" for w in wavs), encoding="utf-8")
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            lst.name,
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            out.name,
        ],
        check=True,
        capture_output=True,
        cwd=str(out.parent),
    )
    for w in wavs:
        w.unlink(missing_ok=True)
    lst.unlink(missing_ok=True)


async def tts(text: str, voice: str, rate: str, out: Path) -> Path:
    await edge_tts.Communicate(text.strip(), voice, rate=rate).save(str(out))
    return out


# Beats: either plain German string, or list of ("de"|"en", text) segments
BEATS: list[tuple[str, object]] = [
    (
        "01_chaos",
        """Jeden Tag dieselbe Belastung.
Zu viele Programme. Doppelte Eingaben. Verlorene Zeit.
Excel. Chat. Stempeluhren. Chaos statt Klarheit.""",
    ),
    (
        "02_turn",
        [
            ("de", "Doch es gibt einen Ausweg. Genau hier setzt"),
            ("en", "Suppix AI"),
            ("de", "an. Ich bin Ihre digitale Begleiterin – und ich zeige Ihnen WorkPass."),
        ],
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
Onboarding und digitale Ausweise – in einem Schritt. Ohne manuellen Wildwuchs.""",
    ),
    (
        "05_employee",
        """Dann der Alltag auf dem Gerät des Mitarbeiters:
QR-Code, NFC oder GPS. Live. Sicher. Revisionssicher.""",
    ),
    (
        "06_ops",
        """Weniger Systeme. Weniger Tippen. Mehr Kontrolle.
Eine Plattform. Eine Wahrheit.""",
    ),
    (
        "07_tax",
        """Und am Monatsende wird aus Betrieb echte Abrechnung:
Steuer, Lohn und Compliance – Teil derselben Kette. Nicht ein weiteres Inselsystem.""",
    ),
    (
        "08_monthend",
        """Am achtundzwanzigsten, dreißigsten oder einunddreißigsten fließen die Daten
automatisch von der Plattform in die Buchhaltung.
Das System empfängt sie – und startet.""",
    ),
    (
        "09_engine",
        """Unser Buchhaltungsmotor verarbeitet enorme Mengen:
bis zu einhunderttausend Mitarbeitende in nur einhundertfünfzehn Sekunden.
Weniger Mitarbeitende – weniger Zeit. Skaliert mit Ihrer Realität.""",
    ),
    (
        "10_dispatch",
        """Er erstellt die Abrechnungen und Kontoauszüge –
und sendet sie aus. Ende-zu-Ende. Ohne manuelles Nachschieben.""",
    ),
    (
        "11_close",
        [
            (
                "de",
                """Acht Sprachen. White-Label. Enterprise-Sicherheit.
Weniger Aufwand. Weniger manuelle Dateneingabe. Mehr Nähe zu Ihrem Team.""",
            ),
            ("en", "Suppix AI."),
            ("de", "Intelligent Work. Connected Future."),
        ],
    ),
]


async def synth_beat(name: str, payload: object) -> tuple[Path, str]:
    BEATS_DIR.mkdir(parents=True, exist_ok=True)
    out = BEATS_DIR / f"{name}.mp3"
    if isinstance(payload, str):
        await tts(payload, VOICE_DE, RATE_DE, out)
        return out, payload.strip()

    parts: list[Path] = []
    plain_bits: list[str] = []
    for i, (lang, text) in enumerate(payload):  # type: ignore[arg-type]
        frag = BEATS_DIR / f"_{name}_{i}_{lang}.mp3"
        if lang == "en":
            await tts(text, VOICE_EN, RATE_EN, frag)
            plain_bits.append(text.strip())
        else:
            await tts(text, VOICE_DE, RATE_DE, frag)
            plain_bits.append(text.strip())
        parts.append(frag)
    concat_mp3(parts, out)
    for p in parts:
        p.unlink(missing_ok=True)
    return out, " ".join(plain_bits)


async def main() -> None:
    meta = []
    files = []
    for name, payload in BEATS:
        path, plain = await synth_beat(name, payload)
        dur = probe(path)
        # Guard: reject absurdly long clips (SSML/regression)
        if dur > 35:
            raise SystemExit(f"{name} too long ({dur:.1f}s) — abort")
        meta.append({"id": name, "file": path.name, "duration": round(dur, 3), "text": plain})
        files.append(path)
        print(f"{name}: {dur:.2f}s")

    lst = BEATS_DIR / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in files), encoding="utf-8")
    full = ROOT / "vo_v8_premium_full.mp3"
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "concat.txt",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(full.name),
        ],
        check=True,
        capture_output=True,
        cwd=str(BEATS_DIR),
    )
    # move if written relative
    produced = BEATS_DIR / full.name
    if produced.exists() and produced.resolve() != full.resolve():
        produced.replace(full)
    (BEATS_DIR / "beats.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FULL {full} {probe(full):.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
