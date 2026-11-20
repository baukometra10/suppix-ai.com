import asyncio
from pathlib import Path

import edge_tts

OUT = Path(__file__).with_name("vo_marlena_style.mp3")

# Warm, clear German neural voice (closest high-quality stand-in until full Marlena master arrives)
VOICE = "de-DE-TanjaNeural"

SCRIPT = """
Guten Tag.

Ich begleite Sie heute durch SUPPIX AI – und durch WorkPass, unsere integrierte Unternehmensplattform.

WorkPass ist kein einzelnes Tool. Es ist eine vollständige Betriebssystem-Schicht für Unternehmen, Organisationen und Behörden: von der Bauwirtschaft über Industrie und Pflege bis zum öffentlichen Sektor.

Alles beginnt mit dem Vertrag. Identität, Onboarding und digitale Ausweise entstehen in einem Schritt. Dann folgt der Alltag: Zutritt mit QR, NFC oder GPS, Live-Anwesenheit, Schichten, Dokumente und Compliance – revisionssicher und mandantenfähig.

Und am Ende des Monats bleibt alles verbunden: Arbeitszeiten fließen in die Lohnkette, bis zur transparenten Abrechnung. Vom Arbeitsvertrag bis zur Gehaltsabrechnung – eine Plattform, ein Prozess, eine Wahrheit.

Acht Sprachen. White-Label. Sicherheit auf Enterprise-Niveau. Weniger Systembrüche. Mehr Kontrolle. Mehr Nähe zu Ihrem Team.

SUPPIX AI. Intelligent Work. Connected Future.
"""


async def main() -> None:
    communicate = edge_tts.Communicate(SCRIPT.strip(), VOICE, rate="-8%")
    await communicate.save(str(OUT))
    print(f"saved {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
