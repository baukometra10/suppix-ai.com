# SUPPIX AI ImageFilm v7 — German premium master

**Brand pronunciation for TTS:** `Suppix Ei-Ai` (English letter names A + I).  
On screen / logo: **SUPPIX.AI**. Do not spell S-U-P-P-I-X.

**Website:** no HTML/JS changes in this pass. AR/EN language variants later.

## Easy paths

| File | Location |
|---|---|
| Final film (~2:20) | `Desktop\Videos\SUPPIX_AI_ImageFilm_Synced.mp4` |
| Full DE VO | `Desktop\Videos\SUPPIX_AI_VO_DE_Premium.mp3` |
| Beat sources | `assets\imagefilm\vo_v7_beats\` |

## Structure (visuals follow speech)

1. **Chaos** — office clutter + multi-app overload  
2. **Turn** — Suppix Ei-Ai / WorkPass introduction  
3. **Platform** — robot + live system dashboard motion  
4. **Contract** — onboarding / Ausweise (OTS typing)  
5. **Employee app** — YouTube short (real product motion)  
6. **Ops** — livemap + speak (less typing, more control)  
7. **Tax / Lohn** — **`workpass-lohn-bridge-de.mp4`** (German tax film) exactly on Steuer/Lohn beat  
8. **Engine** — Buchhaltungsmotor: 100 000 Mitarbeitende in 115 Sekunden  
9. **Close** — languages / less manual entry → **real SUPPIX.AI logo**

## Narration (DE)

### 01 Chaos
Jeden Tag dasselbe Bild.  
Zu viele Programme. Doppelte Eingaben.  
Excel hier. Chat dort. Stempeluhr woanders.  
Die Arbeit wächst – und mit ihr die Last.

### 02 Turn
Genau hier setzt Suppix Ei-Ai an.  
Ich bin Ihre digitale Begleiterin.  
Und ich zeige Ihnen WorkPass – die integrierte Unternehmensplattform.

### 03 Platform
WorkPass ist keine weitere App.  
Es ist die Plattform, die Vertrag, Identität, Zutritt, Anwesenheit und Betrieb verbindet –  
für Unternehmen, Organisationen und Behörden.

### 04 Contract
Alles beginnt mit dem Arbeitsvertrag.  
Onboarding und digitale Ausweise entstehen in einem Schritt –  
ohne manuellen Wildwuchs.

### 05 Employee
Dann der Alltag auf dem Gerät des Mitarbeiters:  
Zutritt mit QR-Code, NFC oder GPS.  
Live. Sicher. Revisionssicher.

### 06 Ops
Weniger Systeme. Weniger Tippen. Mehr Kontrolle.  
Vom Vertrag bis zum Schichtende: eine Wahrheit.

### 07 Tax *(→ German tax video)*
Und die Steuer- und Lohnkette bleibt Teil derselben Plattform.  
Abrechnung, Meldewesen, DATEV-Export –  
verbunden statt zersplittert. Transparent und abschlussbereit.

### 08 Engine
Unser Buchhaltungsmotor verarbeitet enorme Datenmengen:  
bis zu einhunderttausend Mitarbeitende in nur einhundertfünfzehn Sekunden.

### 09 Close
Acht Sprachen. White-Label. Enterprise-Sicherheit.  
Weniger Aufwand. Weniger manuelle Dateneingabe. Mehr Nähe zu Ihrem Team.  
Suppix Ei-Ai.  
Intelligent Work. Connected Future.

## Rebuild

```bash
python assets/imagefilm/make_vo_v7_beats.py
python assets/imagefilm/build_film_v7_premium.py
```
