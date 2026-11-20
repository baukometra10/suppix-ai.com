"""v9: dynamic music ride, Marlena intro, DE/EN/AR masters, 60s ad cut, demo CTA."""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "norm_v9"
VO_DIR = ROOT / "vo_v9"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
MUSIC = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\assets\bg-music.mp3")
MARLENA = ROOT / "marlena_preview.mp3"
SILENT = ROOT / "norm_v8" / "video_silent.mp4"
EXACT = ROOT / "norm_v8"
VIDEOS = Path(r"c:\Users\u4363\Desktop\Videos")
SITE_VIDEOS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\Videos")
DESKTOP = Path(r"c:\Users\u4363\Desktop")

# Visual beat lengths from v8 (must match video_silent)
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

# Music volume ride (absolute linear gain) — rises/falls for drama & clarity
# chaos high → speech duck → monthend lift → proof low → dispatch swell → logo proud then soft
MUSIC_ENV = [
    (0.0, 0.34),
    (17.5, 0.30),
    (18.0, 0.18),
    (82.0, 0.16),
    (95.5, 0.22),
    (110.5, 0.24),
    (111.0, 0.10),  # proof numbers: music down
    (129.0, 0.12),
    (130.0, 0.26),  # dispatch swell
    (141.5, 0.28),
    (150.0, 0.22),
    (158.0, 0.18),
    (167.0, 0.12),
]


def run(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-2500:])


def probe(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    for line in (r.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(path)


def render_music_ride(total: float, out: Path) -> Path:
    """Pre-render music with scene-based volume so levels rise/fall cleanly."""
    # (start, end, volume)
    bands = [
        (0.0, 17.5, 0.36),  # chaos — high drama
        (17.5, 82.0, 0.17),  # solution speech — lower
        (82.0, 110.8, 0.23),  # tax / month-end — lift
        (110.8, 129.5, 0.09),  # proof numbers — very low
        (129.5, 141.5, 0.27),  # dispatch — swell
        (141.5, total, 0.20),  # close / logo
    ]
    parts_dir = OUT / "music_ride_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    for i, (t0, t1, vol) in enumerate(bands):
        if t0 >= total:
            break
        t1 = min(t1, total)
        dur = max(0.05, t1 - t0)
        p = parts_dir / f"band_{i}.wav"
        # Loop source, take segment length, apply volume + edge fades
        fade = min(0.8, dur * 0.15)
        run(
            [
                FFMPEG,
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(MUSIC),
                "-t",
                f"{dur:.3f}",
                "-af",
                f"aformat=sample_rates=44100:channel_layouts=stereo,volume={vol},"
                f"afade=t=in:d={fade:.2f},afade=t=out:st={max(0.05, dur - fade):.2f}:d={fade:.2f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                str(p),
            ]
        )
        parts.append(p)
    lst = parts_dir / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "list.txt",
            "-c",
            "copy",
            str(out.resolve()),
        ],
        cwd=str(parts_dir),
    )
    return out


SCRIPTS: dict[str, dict[str, object]] = {
    "de": {
        "voice": "de-DE-TanjaNeural",
        "rate": "-6%",
        "beats": {
            "01_chaos": """Jeden Tag dieselbe Belastung.
Zu viele Programme. Doppelte Eingaben. Verlorene Zeit.
Excel. Chat. Stempeluhren. Chaos statt Klarheit.""",
            "02_turn": [
                ("de", "Doch es gibt einen Ausweg. Genau hier setzt"),
                ("en", "Suppix AI"),
                ("de", "an. Ich bin Ihre digitale Begleiterin – und ich zeige Ihnen WorkPass."),
            ],
            "03_platform": """WorkPass ist keine weitere App.
Es ist die Plattform, die Vertrag, Identität, Zutritt, Anwesenheit und Betrieb verbindet –
für Unternehmen, Organisationen und Behörden.""",
            "04_contract": """Alles beginnt mit dem Arbeitsvertrag.
Onboarding und digitale Ausweise – in einem Schritt. Ohne manuellen Wildwuchs.""",
            "05_employee": """Dann der Alltag auf dem Gerät des Mitarbeiters:
QR-Code, NFC oder GPS. Live. Sicher. Revisionssicher.""",
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
            "11_close": [
                (
                    "de",
                    """Acht Sprachen. White-Label. Enterprise-Sicherheit.
Weniger Aufwand. Weniger manuelle Dateneingabe.
Erleben Sie den Unterschied in einer persönlichen Demo.""",
                ),
                ("en", "Suppix AI."),
                (
                    "de",
                    "Vereinbaren Sie jetzt Ihren Demo-Termin. Intelligent Work. Connected Future.",
                ),
            ],
        },
    },
    "en": {
        "voice": "en-US-JennyNeural",
        "rate": "-4%",
        "beats": {
            "01_chaos": """Every day, the same pressure.
Too many tools. Double entry. Lost time.
Spreadsheets. Chats. Time clocks. Chaos instead of clarity.""",
            "02_turn": """But there is a way out.
This is where Suppix AI begins.
I am your digital guide — and I’ll show you WorkPass.""",
            "03_platform": """WorkPass is not another app.
It is the platform that connects contracts, identity, access, attendance and operations —
for companies, organizations and public authorities.""",
            "04_contract": """Everything starts with the employment contract.
Onboarding and digital IDs — in one step. Without manual chaos.""",
            "05_employee": """Then the daily work on the employee’s device:
QR, NFC or GPS. Live. Secure. Audit-ready.""",
            "06_ops": """Fewer systems. Less typing. More control.
One platform. One truth.""",
            "07_tax": """And at month-end, operations become real payroll:
tax, wages and compliance — one chain, not another island system.""",
            "08_monthend": """On the twenty-eighth, thirtieth or thirty-first,
data flows automatically from the platform into accounting.
The system receives it — and starts.""",
            "09_engine": """Our accounting engine processes massive volumes:
up to one hundred thousand employees in just one hundred fifteen seconds.
Fewer employees — less time. It scales with your reality.""",
            "10_dispatch": """It creates payslips and statements —
and sends them out. End to end. No manual chasing.""",
            "11_close": """Eight languages. White-label. Enterprise security.
Less effort. Less manual data entry.
See the difference in a personal demo.
Suppix AI.
Book your demo now. Intelligent Work. Connected Future.""",
        },
    },
    "ar": {
        "voice": "ar-SA-ZariyahNeural",
        "rate": "-4%",
        "beats": {
            "01_chaos": """كل يوم نفس الضغط.
برامج كثيرة. إدخال مكرر. وقت ضائع.
جداول. محادثات. ساعات دوام. فوضى بدل الوضوح.""",
            "02_turn": [
                ("de", "لكن هناك مخرج. هنا يبدأ"),
                ("en", "Suppix AI"),
                ("de", "أنا مرافقتكم الرقمية — وأريكم وورك باس."),
            ],
            "03_platform": """وورك باس ليس تطبيقاً إضافياً.
إنه المنصة التي تربط العقد والهوية والدخول والحضور والتشغيل —
للشركات والمؤسسات والجهات الحكومية.""",
            "04_contract": """كل شيء يبدأ بعقد العمل.
التأهيل والبطاقات الرقمية — في خطوة واحدة. بلا فوضى يدوية.""",
            "05_employee": """ثم يوم الموظف على جهازه:
رمز الاستجابة أو إن إف سي أو جي بي إس. مباشر. آمن. قابل للتدقيق.""",
            "06_ops": """أنظمة أقل. كتابة أقل. رقابة أكثر.
منصة واحدة. حقيقة واحدة.""",
            "07_tax": """وفي نهاية الشهر يصبح التشغيل محاسبة حقيقية:
الضرائب والأجور والامتثال — سلسلة واحدة لا جزراً منفصلة.""",
            "08_monthend": """في اليوم الثامن والعشرين أو الثلاثين أو الحادي والثلاثين
تتدفق البيانات تلقائياً من المنصة إلى المحاسبة.
يستلمها النظام — ويبدأ.""",
            "09_engine": """محرك المحاسبة لدينا يعالج أحجاماً هائلة:
حتى مئة ألف موظف في مئة وخمس عشرة ثانية فقط.
كلما قل العدد قل الزمن. يتوسع مع واقعكم.""",
            "10_dispatch": """ينشئ كشوف الرواتب وكشوف الحساب —
ويرسلها. من البداية للنهاية. بلا مطاردة يدوية.""",
            "11_close": [
                (
                    "de",
                    """ثماني لغات. علامة بيضاء. أمان للمؤسسات.
جهد أقل. إدخال يدوي أقل.
اختبروا الفرق في عرض توضيحي شخصي.""",
                ),
                ("en", "Suppix AI."),
                ("de", "احجزوا موعد العرض الآن. عمل ذكي. مستقبل متصل."),
            ],
        },
    },
}


async def tts(text: str, voice: str, rate: str, out: Path) -> None:
    await edge_tts.Communicate(text.strip(), voice, rate=rate).save(str(out))


async def synth_payload(lang: str, beat_id: str, payload: object, out: Path) -> None:
    cfg = SCRIPTS[lang]
    voice = cfg["voice"]
    rate = cfg["rate"]
    if isinstance(payload, str):
        await tts(payload, voice, rate, out)
        return
    # mixed segments (DE brand)
    parts = []
    for i, (seg_lang, text) in enumerate(payload):  # type: ignore
        frag = out.parent / f"_{lang}_{beat_id}_{i}.mp3"
        if seg_lang == "en":
            await tts(text, "en-US-JennyNeural", "-2%", frag)
        else:
            await tts(text, voice, rate, frag)
        parts.append(frag)
    wavs = []
    for i, p in enumerate(parts):
        w = out.parent / f"_{lang}_{beat_id}_{i}.wav"
        run(
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
            ]
        )
        wavs.append(w)
    lst = out.parent / f"_{lang}_{beat_id}_list.txt"
    lst.write_text("".join(f"file '{w.name}'\n" for w in wavs), encoding="utf-8")
    run(
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
        cwd=str(out.parent),
    )
    for p in parts + wavs:
        p.unlink(missing_ok=True)
    lst.unlink(missing_ok=True)


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
    else:
        # slight speed-up if a bit long, else trim
        if dur > target * 1.12:
            factor = dur / target
            run(
                [
                    FFMPEG,
                    "-y",
                    "-i",
                    str(src),
                    "-af",
                    f"atempo={min(1.25, factor):.4f}",
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


async def build_lang_voice(lang: str) -> Path:
    VO_DIR.mkdir(parents=True, exist_ok=True)
    lang_dir = VO_DIR / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    beats = SCRIPTS[lang]["beats"]
    aligned = []
    for beat_id, target in BEAT_ORDER:
        raw = lang_dir / f"{beat_id}_raw.mp3"
        print(f"TTS {lang}/{beat_id} ...")
        await synth_payload(lang, beat_id, beats[beat_id], raw)
        # DE chaos: lead with Marlena preview for authentic presence
        if lang == "de" and beat_id == "01_chaos" and MARLENA.exists():
            merged = lang_dir / "01_chaos_with_marlena.mp3"
            m_wav = lang_dir / "_m.wav"
            c_wav = lang_dir / "_c.wav"
            gap = lang_dir / "_g.wav"
            for src, dst, af in (
                (MARLENA, m_wav, "loudnorm=I=-16:TP=-1.5:LRA=11"),
                (raw, c_wav, "loudnorm=I=-16:TP=-1.5:LRA=11"),
            ):
                run(
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
                    ]
                )
            run(
                [
                    FFMPEG,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=44100:cl=mono",
                    "-t",
                    "0.25",
                    str(gap),
                ]
            )
            lst = lang_dir / "_mc.txt"
            lst.write_text(
                f"file '{m_wav.name}'\nfile '{gap.name}'\nfile '{c_wav.name}'\n",
                encoding="utf-8",
            )
            run(
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
                    merged.name,
                ],
                cwd=str(lang_dir),
            )
            raw = merged
        fit = lang_dir / f"{beat_id}.wav"
        fit_audio(raw, fit, target)
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
    return voice


def mux_dynamic(video: Path, voice: Path, out: Path, music_ride: Path) -> None:
    """Scene-ridden music + sidechain duck under speech for demo-ready dynamics."""
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
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(video),
            "-i",
            str(voice),
            "-i",
            str(music_ride),
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
            "-movflags",
            "+faststart",
            str(out),
        ]
    )


def make_playable(src: Path, dst: Path) -> None:
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(src),
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
            str(dst),
        ]
    )


def build_short_ad(full: Path, out: Path) -> None:
    """~55s high-drama cut: chaos → solution → tax/engine proof → demo CTA/logo."""
    # Pick ranges from full timeline
    # 0-8 chaos, 17.5-25 turn, 95.7-114 monthend+engine start, 111-125 proof, 141.5-167 close
    parts_dir = OUT / "short_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    clips = [
        (0.0, 8.0, "s1"),
        (17.5, 8.0, "s2"),
        (95.7, 10.0, "s3"),
        (111.0, 12.0, "s4"),
        (145.0, 17.0, "s5"),
    ]
    paths = []
    for ss, dur, name in clips:
        p = parts_dir / f"{name}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-ss",
                f"{ss:.3f}",
                "-i",
                str(full),
                "-t",
                f"{dur:.3f}",
                "-vf",
                "fade=t=in:st=0:d=0.25,fade=t=out:st={fo:.2f}:d=0.3,fps=24,format=yuv420p".format(
                    fo=max(0.2, dur - 0.3)
                ),
                "-af",
                "afade=t=in:d=0.2,afade=t=out:st={fo:.2f}:d=0.3".format(fo=max(0.2, dur - 0.3)),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-profile:v",
                "main",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                str(p),
            ]
        )
        paths.append(p)
    lst = parts_dir / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in paths), encoding="utf-8")
    raw = parts_dir / "short_raw.mp4"
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "list.txt",
            "-c",
            "copy",
            "short_raw.mp4",
        ],
        cwd=str(parts_dir),
    )
    # Boost music presence on short: remux with stronger bed on extracted audio is hard;
    # instead loudnorm final for punchy ad feel
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(raw),
            "-af",
            "loudnorm=I=-14:TP=-1.0:LRA=9",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
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


async def main_async() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not SILENT.exists():
        raise SystemExit(f"missing {SILENT}")

    voices = {}
    for lang in ("de", "en", "ar"):
        vpath = VO_DIR / lang / "voice_aligned.wav"
        if vpath.exists() and abs(probe(vpath) - probe(SILENT)) < 1.5:
            print(f"reuse voice {lang}")
            voices[lang] = vpath
        else:
            voices[lang] = await build_lang_voice(lang)
        print(f"voice {lang}: {probe(voices[lang]):.2f}s")

    total = probe(SILENT)
    music_ride = OUT / "music_ride.wav"
    print("render music ride ...")
    render_music_ride(total, music_ride)

    outputs = {}
    for lang in ("de", "en", "ar"):
        tmp = OUT / f"film_{lang}_mux.mp4"
        play = OUT / f"SUPPIX_AI_ImageFilm_{lang.upper()}.mp4"
        print(f"mux {lang} with dynamic music ...")
        mux_dynamic(SILENT, voices[lang], tmp, music_ride)
        make_playable(tmp, play)
        outputs[lang] = play
        publish(
            play,
            f"SUPPIX_AI_ImageFilm_{lang.upper()}.mp4",
            *(["SUPPIX_AI_ImageFilm_PLAY.mp4", "SUPPIX_AI_ImageFilm_Synced.mp4"] if lang == "de" else []),
        )

    short = OUT / "SUPPIX_AI_ImageFilm_AD_60s.mp4"
    print("building short ad ...")
    build_short_ad(outputs["de"], short)
    publish(short, "SUPPIX_AI_ImageFilm_AD_60s.mp4")
    shutil.copy2(short, DESKTOP / "SUPPIX_AI_ImageFilm_AD_60s.mp4")

    # VO exports
    for lang in ("de", "en", "ar"):
        vo_mp3 = VO_DIR / lang / "voice_full.mp3"
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(voices[lang]),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(vo_mp3),
            ]
        )
        publish(vo_mp3, f"SUPPIX_AI_VO_{lang.upper()}_Premium.mp3")

    print("DONE")
    for lang, p in outputs.items():
        print(lang, probe(p), p.stat().st_size)
    print("short", probe(short), short.stat().st_size)


if __name__ == "__main__":
    asyncio.run(main_async())
