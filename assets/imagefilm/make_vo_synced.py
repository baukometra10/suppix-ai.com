"""Professional German VO with correct brand pronunciation: Suppix AI."""
import asyncio
from pathlib import Path

import edge_tts

OUT = Path(__file__).with_name("vo_synced_professional.mp3")
VOICE = "de-DE-TanjaNeural"

# Phonetic brand: "Suppix AI" (not letter-spelled SUPPIX; AI as A-I)
# Written for neural TTS clarity.
SCRIPT = """
Guten Tag.

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

Suppix AI.
Intelligent Work. Connected Future.
"""


async def main() -> None:
    communicate = edge_tts.Communicate(SCRIPT.strip(), VOICE, rate="-10%")
    await communicate.save(str(OUT))
    print(f"saved {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
