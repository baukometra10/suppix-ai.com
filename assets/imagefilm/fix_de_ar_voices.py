"""Fix DE (one consistent voice, no Marlena) + clearer AR pronunciation; remux films."""
from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "norm_v9"
VO = ROOT / "vo_v9_fixed"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SILENT = ROOT / "norm_v8" / "video_silent.mp4"
MUSIC = OUT / "music_ride.wav"
VIDEOS = Path(r"c:\Users\u4363\Desktop\Videos")
SITE_VIDEOS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\Videos")

BEAT_ORDER = [
    ("01_chaos", 17.54),
    ("02_turn", 14.13),
    ("03_platform", 16.04),
    ("04_contract", 10.75),
    ("05_employee", 13.33),
    ("06_ops", 10.50),
    ("07_tax", 13.42),
    ("08_monthend", 15.08),
    ("09_engine", 18.79),
    ("10_dispatch", 12.00),
    ("11_close", 25.46),
]

# Single German voice end-to-end. Brand: letter-by-letter A-I for clarity.
DE = {
    "voice": "de-DE-TanjaNeural",
    "rate": "-6%",
    "beats": {
        "01_chaos": """Jeden Tag dieselbe Belastung.
Zu viele Programme. Doppelte Eingaben. Verlorene Zeit.
Excel. Chat. Stempeluhren. Chaos statt Klarheit.""",
        "02_turn": """Doch es gibt einen Ausweg.
Genau hier setzt Suppix A-I an.
Ich bin Ihre digitale Begleiterin – und ich zeige Ihnen WorkPass.""",
        "03_platform": """WorkPass ist keine weitere App.
Es ist die Plattform, die Vertrag, Identität, Zutritt, Anwesenheit und Betrieb verbindet –
für Unternehmen, Organisationen und Behörden.""",
        "04_contract": """Alles beginnt mit dem Arbeitsvertrag.
Onboarding und digitale Ausweise – in einem Schritt. Ohne manuellen Wildwuchs.""",
        "05_employee": """Dann der Alltag auf dem Gerät des Mitarbeiters:
QR-Code, N-F-C oder G-P-S. Live. Sicher. Revisionssicher.""",
        "06_ops": """Weniger Systeme. Weniger Tippen. Mehr Kontrolle.
Eine Plattform. Eine Wahrheit.""",
        "07_tax": """Und am Monatsende wird aus Betrieb echte Abrechnung:
Steuer, Lohn und Compliance – Teil derselben Kette. Nicht ein weiteres Inselsystem.""",
        "08_monthend": """Am achtundzwanzigsten, dreißigsten oder einunddreißigsten fließen die Daten
automatisch von der Plattform in die Buchhaltung.
Das System empfängt sie – und startet.""",
        "09_engine": """Unser Buchhaltungsmotor verarbeitet enorme Mengen:
bis zu einhunderttausend Mitarbeitende in nur einhundertfünfzehn Sekunden.
Weniger Mitarbeitende – weniger Zeit. Skaliert mit Ihrer Realität.""",
        "10_dispatch": """Er erstellt die Abrechnungen und Kontoauszüge –
und sendet sie aus. Ende-zu-Ende. Ohne manuelles Nachschieben.""",
        "11_close": """Acht Sprachen. White-Label. Enterprise-Sicherheit.
Weniger Aufwand. Weniger manuelle Dateneingabe.
Erleben Sie den Unterschied in einer persönlichen Demo.
Suppix A-I.
Vereinbaren Sie jetzt Ihren Demo-Termin.
Intelligent Work. Connected Future.""",
    },
}

# Arabic: clearer MSA + phonetic foreign terms for neural TTS
# Voice: Egyptian Salma is often clearer for formal marketing narration
AR = {
    "voice": "ar-EG-SalmaNeural",
    "rate": "-2%",
    "beats": {
        "01_chaos": """كُلَّ يَوْمٍ نَفْسُ الضَّغْطِ.
بَرامِجُ كَثيرَةٌ. إِدْخالٌ مُكَرَّرٌ. وَقْتٌ ضائِعٌ.
جَداوِلُ حِسابٍ. مُحادَثاتٌ. ساعاتُ دوامٍ. فَوْضىً بَدَلَ الوُضوحِ.""",
        "02_turn": """لكِنْ هُناكَ مَخْرَجٌ.
هُنا يَبْدَأُ سابِكْس إِي-آي.
أَنا مُرافِقَتُكُم الرَّقْمِيَّةُ، وَأُريكُمْ ووركْ باس.""",
        "03_platform": """ووركْ باس لَيْسَ تَطْبيقًا إِضافِيًّا.
إِنَّهُ المِنَصَّةُ الَّتي تَرْبِطُ العَقْدَ وَالهُوِيَّةَ وَالدُّخولَ وَالحُضورَ وَالتَّشْغيلَ،
لِلشَّرِكاتِ وَالمُؤَسَّساتِ وَالجِهاتِ الحُكومِيَّةِ.""",
        "04_contract": """كُلُّ شَيْءٍ يَبْدَأُ بِعَقْدِ العَمَلِ.
التَّأْهيلُ وَالبِطاقاتُ الرَّقْمِيَّةُ في خُطْوَةٍ واحِدَةٍ، بِلا فَوْضىً يَدَوِيَّةٍ.""",
        "05_employee": """ثُمَّ يَوْمُ المُوَظَّفِ عَلى جِهازِهِ:
كْيو آر، أَوْ إِنْ إِفْ سي، أَوْ جي بي إِسْ.
مُباشِرٌ. آمِنٌ. قابِلٌ لِلتَّدْقيقِ.""",
        "06_ops": """أَنْظِمَةٌ أَقَلُّ. كِتابَةٌ أَقَلُّ. رَقابَةٌ أَكْثَرُ.
مِنَصَّةٌ واحِدَةٌ. حَقيقَةٌ واحِدَةٌ.""",
        "07_tax": """وَفي نِهايَةِ الشَّهْرِ يُصْبِحُ التَّشْغيلُ مُحاسَبَةً حَقيقِيَّةً:
الضَّرائِبُ وَالأُجورُ وَالالْتِزامُ، سِلْسِلَةٌ واحِدَةٌ لا جُزُرًا مُنْفَصِلَةً.""",
        "08_monthend": """في اليَوْمِ الثّامِنِ وَالعِشْرينَ، أَوِ الثَّلاثينَ، أَوِ الحادي وَالثَّلاثينَ،
تَتَدَفَّقُ البَياناتُ تِلْقائِيًّا مِنَ المِنَصَّةِ إِلى المُحاسَبَةِ.
يَسْتَلِمُها النِّظامُ، ثُمَّ يَبْدَأُ.""",
        "09_engine": """مُحَرِّكُ المُحاسَبَةِ لَدَيْنا يُعالِجُ أَحْجامًا هائِلَةً:
حَتّى مِئَةِ أَلْفِ مُوَظَّفٍ في مِئَةٍ وَخَمْسَ عَشْرَةَ ثانِيَةً فَقَطْ.
كُلَّما قَلَّ العَدَدُ قَلَّ الزَّمَنُ. يَتَوَسَّعُ مَعَ واقِعِكُمْ.""",
        "10_dispatch": """يُنْشِئُ كُشوفَ الرَّواتِبِ وَكُشوفَ الحِسابِ،
ثُمَّ يُرْسِلُها مِنَ البِدايَةِ إِلى النِّهايَةِ، بِلا مُتابَعَةٍ يَدَوِيَّةٍ.""",
        "11_close": """ثَماني لُغاتٍ. وايْت ليبِل. أَمانٌ لِلمُؤَسَّساتِ.
جُهْدٌ أَقَلُّ. إِدْخالٌ يَدَوِيٌّ أَقَلُّ.
اخْتَبِروا الفَرْقَ في عَرْضٍ تَوْضيحيٍّ شَخْصيٍّ.
سابِكْس إِي-آي.
احْجِزوا مَوْعِدَ العَرْضِ الآنَ.
عَمَلٌ ذَكِيٌّ. مُسْتَقْبَلٌ مُتَّصِلٌ.""",
    },
}


def run(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-2200:])


def probe(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(path)


def fit_audio(src: Path, dst: Path, target: float) -> None:
    dur = probe(src)
    if dur < target - 0.05:
        pad = target - dur
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(src),
                "-af",
                f"apad=pad_dur={pad:.3f}",
                "-t",
                f"{target:.3f}",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dst),
            ]
        )
    elif dur > target * 1.12:
        factor = min(1.22, dur / target)
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(src),
                "-af",
                f"atempo={factor:.4f}",
                "-t",
                f"{target:.3f}",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dst),
            ]
        )
    else:
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(src),
                "-t",
                f"{target:.3f}",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dst),
            ]
        )


async def build_voice(lang: str, cfg: dict) -> Path:
    lang_dir = VO / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    aligned = []
    for beat_id, target in BEAT_ORDER:
        raw = lang_dir / f"{beat_id}.mp3"
        text = cfg["beats"][beat_id]
        print(f"{lang}/{beat_id} ...")
        await edge_tts.Communicate(text.strip(), cfg["voice"], rate=cfg["rate"]).save(str(raw))
        # Normalize loudness for one stable voice presence
        norm = lang_dir / f"{beat_id}_n.wav"
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(raw),
                "-af",
                "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(norm),
            ]
        )
        fit = lang_dir / f"{beat_id}.wav"
        fit_audio(norm, fit, target)
        aligned.append(fit)

    voice = lang_dir / "voice_aligned.wav"
    lst = lang_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in aligned), encoding="utf-8")
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "concat.txt",
            "-c",
            "copy",
            "voice_aligned.wav",
        ],
        cwd=str(lang_dir),
    )
    print(f"{lang} voice {probe(voice):.2f}s")
    return voice


def mux(video: Path, voice: Path, music: Path, out: Path) -> None:
    total = probe(video)
    filt = (
        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.1,"
        f"apad=whole_dur={total:.3f},asplit=2[vo_sc][vo_mix];"
        f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,"
        f"apad=whole_dur={total:.3f}[musride];"
        f"[musride][vo_sc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=320:makeup=1.35:mix=0.88[mus];"
        f"[vo_mix][mus]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
        f"alimiter=limit=0.94[a]"
    )
    tmp = out.with_suffix(".mux.mp4")
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(video),
            "-i",
            str(voice),
            "-i",
            str(music),
            "-filter_complex",
            filt,
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(tmp),
        ]
    )
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(tmp),
            "-c:v",
            "libx264",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(out),
        ]
    )


def publish(src: Path, *names: str) -> None:
    for base in (VIDEOS, SITE_VIDEOS, ROOT):
        base.mkdir(parents=True, exist_ok=True)
        for name in names:
            shutil.copy2(src, base / name)
            print("copied", base / name)


async def main() -> None:
    if not SILENT.exists() or not MUSIC.exists():
        raise SystemExit("missing silent video or music_ride")

    de_voice = await build_voice("de", DE)
    ar_voice = await build_voice("ar", AR)

    de_out = OUT / "SUPPIX_AI_ImageFilm_DE.mp4"
    ar_out = OUT / "SUPPIX_AI_ImageFilm_AR.mp4"
    print("mux DE ...")
    mux(SILENT, de_voice, MUSIC, de_out)
    print("mux AR ...")
    mux(SILENT, ar_voice, MUSIC, ar_out)

    publish(de_out, "SUPPIX_AI_ImageFilm_DE.mp4", "SUPPIX_AI_ImageFilm_PLAY.mp4", "SUPPIX_AI_ImageFilm_Synced.mp4")
    publish(ar_out, "SUPPIX_AI_ImageFilm_AR.mp4")

    # Export fixed VO samples for listening
    for lang, voice in (("de", de_voice), ("ar", ar_voice)):
        mp3 = VO / lang / "voice_full.mp3"
        run([FFMPEG, "-y", "-i", str(voice), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3)])
        publish(mp3, f"SUPPIX_AI_VO_{lang.upper()}_Premium.mp3")
        # first 15s check
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(voice),
                "-t",
                "15",
                "-c:a",
                "libmp3lame",
                str(VIDEOS / f"CHECK_{lang.upper()}_start_15s.mp3"),
            ]
        )

    print("DONE", probe(de_out), probe(ar_out))


if __name__ == "__main__":
    asyncio.run(main())
