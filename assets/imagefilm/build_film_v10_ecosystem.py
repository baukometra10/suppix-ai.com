"""v10: correct payslip flow (accounting→platform review→employee app) + ecosystem (chat/meetings/cameras/AI/4-eyes).

Rebuilds silent montage + DE/EN/AR VO (one voice each) + dynamic music.
"""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
CURSOR = Path(r"C:\Users\u4363\.cursor\projects\c-Users-u4363-Desktop-Suppix-AI-website\assets")
SITE = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\assets")
OUT = ROOT / "norm_v10"
VO_DIR = ROOT / "vo_v10"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
MUSIC_SRC = SITE / "bg-music.mp3"
LOGO = ROOT / "endcard_logo_real.png"
TAX_DE = SITE / "workpass-lohn-bridge-de.mp4"
VIDEOS = Path(r"c:\Users\u4363\Desktop\Videos")
SITE_VIDEOS = Path(r"c:\Users\u4363\Desktop\Suppix-AI.website\Videos")

# Visual plan: id -> approximate target seconds (VO will be fitted)
PLAN = [
    "01_chaos",
    "02_turn",
    "03_platform",
    "04_contract",
    "05_employee",
    "06_ops",
    "07_tax",
    "08_monthend",
    "09_engine",
    "10_review",  # corrected flow
    "11_ecosystem",  # chat/meetings/cameras/AI/4-eyes
    "12_close",
]


def find(name: str) -> Path:
    for b in (ROOT, CURSOR, SITE):
        p = b / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


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


def norm(src: Path, dst: Path, seconds: float, *, ss: float | None = None, kind: str = "sol") -> None:
    need = max(0.5, seconds)
    src_dur = probe(src)
    cmd = [FFMPEG, "-y"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    if src_dur + 0.1 < need:
        cmd += ["-stream_loop", "-1"]
    cmd += ["-i", str(src), "-t", f"{need:.3f}"]
    if kind == "chaos":
        grade = "eq=contrast=1.15:brightness=-0.05:saturation=0.75"
    elif kind == "proof":
        grade = "eq=contrast=1.1:brightness=0.04:saturation=1.05"
    else:
        grade = "eq=contrast=1.05:brightness=0.03:saturation=1.04"
    fi = min(0.35, need * 0.12)
    fo = min(0.35, need * 0.12)
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24,format=yuv420p,setsar=1,"
        f"{grade},fade=t=in:st=0:d={fi:.2f},fade=t=out:st={max(0.05, need - fo):.2f}:d={fo:.2f}"
    )
    run(
        cmd
        + [
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            str(dst),
        ]
    )


def xfade(a: Path, b: Path, dst: Path, ov: float = 0.35) -> None:
    da, db = probe(a), probe(b)
    o = min(ov, da * 0.2, db * 0.2)
    off = max(0.05, da - o)
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(a),
            "-i",
            str(b),
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration={o:.3f}:offset={off:.3f},format=yuv420p[v]",
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-profile:v",
            "main",
            str(dst),
        ]
    )


def logo_card(dst: Path, seconds: float) -> None:
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24,format=yuv420p,setsar=1,"
        f"fade=t=in:st=0:d=1.0,fade=t=out:st={max(0.4, seconds - 1.0):.2f}:d=1.0"
    )
    run(
        [
            FFMPEG,
            "-y",
            "-loop",
            "1",
            "-i",
            str(LOGO),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dst),
        ]
    )


def proof_overlay(src: Path, dst: Path, seconds: float) -> None:
    start = max(0.4, seconds * 0.2)
    dur = min(4.2, seconds * 0.5)

    def esc(t: str) -> str:
        return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

    draw = (
        f"drawtext=text='{esc('100.000 Mitarbeitende')}':fontsize=64:fontcolor=white:borderw=3:bordercolor=black@0.55:"
        f"x=(w-text_w)/2:y=(h*0.38):enable='between(t\\,{start:.2f}\\,{start + dur:.2f})',"
        f"drawtext=text='{esc('115 Sekunden')}':fontsize=78:fontcolor=0x7DD3FC:borderw=3:bordercolor=black@0.55:"
        f"x=(w-text_w)/2:y=(h*0.50):enable='between(t\\,{start:.2f}\\,{start + dur:.2f})'"
    )
    # re-encode with overlay
    run(
        [
            FFMPEG,
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(src),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=24,format=yuv420p,setsar=1,"
            f"eq=contrast=1.1:brightness=0.04:saturation=1.05,{draw}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-profile:v",
            "main",
            str(dst),
        ]
    )


def build_visual(bid: str, seconds: float, dst: Path) -> None:
    chaos_office = find("chaos_office.mp4")
    chaos_apps = find("chaos_apps.mp4")
    chaos_to = find("chaos_to_solution.mp4")
    solution = find("solution_calm.mp4")
    monthend = find("monthend_flow.mp4")
    accounting = find("accounting_process.mp4")
    engine = find("engine_power.mp4")
    four = find("four_eyes_verify.mp4")
    cams = find("cameras_ai_ops.mp4")
    comms = find("comms_meetings.mp4")
    dash = find("sys_review_dashboard.mp4")
    app = find("sys_employee_app.mp4")
    livemap = find("sys_livemap_ops.mp4")
    speak = ROOT / "suppix-v4-speak.mp4"
    speak2 = ROOT / "suppix-v4-speak2.mp4"
    speak3 = ROOT / "suppix-v4-speak3.mp4"
    typing = ROOT / "suppix-v4-ots-type.mp4"
    work = ROOT / "suppix-v4-ots-work.mp4"
    employee = ROOT / "employee_app_insert.mp4"
    dispatch = ROOT / "payslip_dispatch.mp4"
    review_send = CURSOR / "payslip_review_send.mp4"
    if not review_send.exists():
        review_send = ROOT / "payslip_review_send.mp4"

    def pair(a_src: Path, b_src: Path, ka="sol", kb="sol", ss_b: float | None = None) -> None:
        a = OUT / f"_{bid}_a.mp4"
        b = OUT / f"_{bid}_b.mp4"
        norm(a_src, a, seconds * 0.55 + 0.4, kind=ka)
        norm(b_src, b, seconds * 0.55 + 0.4, ss=ss_b, kind=kb)
        mid = OUT / f"_{bid}_xf.mp4"
        xfade(a, b, mid, 0.35)
        norm(mid, dst, seconds, kind=kb)

    if bid == "01_chaos":
        pair(chaos_office, chaos_apps, "chaos", "chaos")
    elif bid == "02_turn":
        pair(chaos_to, speak if speak.exists() else solution, "chaos", "sol")
    elif bid == "03_platform":
        pair(work if work.exists() else solution, dash, "sol", "sol")
    elif bid == "04_contract":
        norm(typing if typing.exists() else work, dst, seconds)
    elif bid == "05_employee":
        norm(employee, dst, seconds)
    elif bid == "06_ops":
        pair(livemap, speak2 if speak2.exists() else dash)
    elif bid == "07_tax":
        norm(TAX_DE, dst, seconds, ss=100.0, kind="sol")
    elif bid == "08_monthend":
        pair(monthend, TAX_DE, "sol", "sol", ss_b=120.0)
    elif bid == "09_engine":
        tmp = OUT / "_eng_raw.mp4"
        a = OUT / "_eng_a.mp4"
        b = OUT / "_eng_b.mp4"
        norm(accounting, a, seconds * 0.55 + 0.4, kind="proof")
        norm(engine, b, seconds * 0.55 + 0.4, kind="proof")
        xfade(a, b, tmp, 0.35)
        proof_overlay(tmp, dst, seconds)
    elif bid == "10_review":
        # accounting → platform review → employee app
        a = OUT / "_rv_a.mp4"
        b = OUT / "_rv_b.mp4"
        c = OUT / "_rv_c.mp4"
        mid1 = OUT / "_rv_m1.mp4"
        third = seconds / 3 + 0.5
        if review_send.exists():
            norm(review_send, a, seconds * 0.4 + 0.4)
            norm(dash, b, seconds * 0.35 + 0.4)
            norm(app, c, seconds * 0.4 + 0.4)
        else:
            norm(dispatch if dispatch.exists() else accounting, a, third, kind="sol")
            norm(four, b, third, kind="sol")
            norm(app, c, third, kind="sol")
        xfade(a, b, mid1, 0.3)
        mid2 = OUT / "_rv_m2.mp4"
        xfade(mid1, c, mid2, 0.35)
        norm(mid2, dst, seconds)
    elif bid == "11_ecosystem":
        # comms + cameras/AI + four-eyes
        a = OUT / "_eco_a.mp4"
        b = OUT / "_eco_b.mp4"
        c = OUT / "_eco_c.mp4"
        mid1 = OUT / "_eco_m1.mp4"
        norm(comms, a, seconds * 0.4 + 0.4)
        norm(cams, b, seconds * 0.4 + 0.4)
        norm(four, c, seconds * 0.4 + 0.4)
        xfade(a, b, mid1, 0.3)
        mid2 = OUT / "_eco_m2.mp4"
        xfade(mid1, c, mid2, 0.35)
        norm(mid2, dst, seconds)
    elif bid == "12_close":
        speak_dur = max(4.0, min(seconds * 0.45, seconds - 5.5))
        logo_dur = max(5.5, seconds - speak_dur + 0.5)
        a = OUT / "_cl_a.mp4"
        b = OUT / "_cl_b.mp4"
        norm(speak3 if speak3.exists() else speak, a, speak_dur)
        logo_card(b, logo_dur)
        mid = OUT / "_cl_xf.mp4"
        xfade(a, b, mid, 0.65)
        norm(mid, dst, seconds)
    else:
        raise KeyError(bid)


SCRIPTS = {
    "de": {
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
            "10_review": """Danach kommen die Abrechnungen zurück auf die Plattform.
Dort werden sie geprüft und freigegeben – erst dann gehen sie an die Mitarbeiter-App.
Kontrolle vor Zustellung. Klar und nachvollziehbar.""",
            "11_ecosystem": """Und WorkPass ist mehr als Abrechnung.
Chat, Anrufe und Video-Meetings. Kameras und KI. Verifizierung und das Vier-Augen-Prinzip.
Ein System, das viele Einzellösungen ersetzt.""",
            "12_close": """Acht Sprachen. White-Label. Enterprise-Sicherheit.
Weniger Aufwand. Weniger manuelle Dateneingabe.
Erleben Sie den Unterschied in einer persönlichen Demo.
Suppix A-I.
Vereinbaren Sie jetzt Ihren Demo-Termin.
Intelligent Work. Connected Future.""",
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
This is where Suppix A-I begins.
I am your digital guide — and I’ll show you WorkPass.""",
            "03_platform": """WorkPass is not another app.
It is the platform that connects contracts, identity, access, attendance and operations —
for companies, organizations and public authorities.""",
            "04_contract": """Everything starts with the employment contract.
Onboarding and digital IDs — in one step. Without manual chaos.""",
            "05_employee": """Then the daily work on the employee’s device:
QR code, N-F-C or G-P-S. Live. Secure. Audit-ready.""",
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
            "10_review": """Then the statements return to the platform.
They are reviewed and approved — and only then sent to the employee app.
Control before delivery. Clear and traceable.""",
            "11_ecosystem": """And WorkPass is more than payroll.
Chat, calls and video meetings. Cameras and A-I. Verification and the four-eyes principle.
One system that replaces many separate tools.""",
            "12_close": """Eight languages. White-label. Enterprise security.
Less effort. Less manual data entry.
See the difference in a personal demo.
Suppix A-I.
Book your demo now.
Intelligent Work. Connected Future.""",
        },
    },
    "ar": {
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
            "10_review": """ثُمَّ تَعودُ الكُشوفُ إِلى المِنَصَّةِ.
تُراجَعُ وَتُعْتَمَدُ، وَبَعْدَها فَقَطْ تُرْسَلُ إِلى تَطْبيقِ المُوَظَّفِ.
رَقابَةٌ قَبْلَ التَّوْصيلِ. واضِحَةٌ وَقابِلَةٌ لِلتَّتَبُّعِ.""",
            "11_ecosystem": """وَووركْ باس أَكْثَرُ مِنَ المُحاسَبَةِ.
دَرْدَشَةٌ وَمُكالَماتٌ وَاجْتِماعاتُ فيديو. كاميراتٌ وَذَكاءٌ اصْطِناعيٌّ. تَحَقُّقٌ وَمَبْدَأُ الأَرْبَعِ عُيونٍ.
نِظامٌ واحِدٌ يُغنيكُمْ عَنْ أَدَواتٍ كَثيرَةٍ.""",
            "12_close": """ثَماني لُغاتٍ. وايْت ليبِل. أَمانٌ لِلمُؤَسَّساتِ.
جُهْدٌ أَقَلُّ. إِدْخالٌ يَدَوِيٌّ أَقَلُّ.
اخْتَبِروا الفَرْقَ في عَرْضٍ تَوْضيحيٍّ شَخْصيٍّ.
سابِكْس إِي-آي.
احْجِزوا مَوْعِدَ العَرْضِ الآنَ.
عَمَلٌ ذَكِيٌّ. مُسْتَقْبَلٌ مُتَّصِلٌ.""",
        },
    },
}


async def tts_beat(text: str, voice: str, rate: str, out: Path) -> None:
    await edge_tts.Communicate(text.strip(), voice, rate=rate).save(str(out))


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
                f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur={pad:.3f}",
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
                f"loudnorm=I=-16:TP=-1.5:LRA=11,atempo={factor:.4f}",
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
                "-af",
                "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-t",
                f"{target:.3f}",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dst),
            ]
        )


async def synth_all_languages() -> dict[str, dict[str, Path]]:
    """Return lang -> beat_id -> raw mp3 path, and natural durations."""
    VO_DIR.mkdir(parents=True, exist_ok=True)
    raws: dict[str, dict[str, Path]] = {}
    for lang, cfg in SCRIPTS.items():
        lang_dir = VO_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        raws[lang] = {}
        for bid in PLAN:
            out = lang_dir / f"{bid}.mp3"
            print(f"TTS {lang}/{bid}")
            await tts_beat(cfg["beats"][bid], cfg["voice"], cfg["rate"], out)
            raws[lang][bid] = out
    return raws


def choose_durations(raws: dict[str, dict[str, Path]]) -> dict[str, float]:
    """Pick visual duration per beat from max of three languages + padding."""
    pads = {
        "01_chaos": 0.1,
        "02_turn": 0.2,
        "03_platform": 0.2,
        "04_contract": 0.15,
        "05_employee": 0.15,
        "06_ops": 0.15,
        "07_tax": 0.8,
        "08_monthend": 0.6,
        "09_engine": 1.0,
        "10_review": 0.8,
        "11_ecosystem": 0.8,
        "12_close": 3.8,
    }
    durs = {}
    for bid in PLAN:
        mx = max(probe(raws[lang][bid]) for lang in raws)
        durs[bid] = mx + pads.get(bid, 0.2)
    return durs


def render_music_ride(total: float, out: Path) -> Path:
    bands = [
        (0.0, 0.12, 0.34),
        (0.12, 0.48, 0.16),
        (0.48, 0.66, 0.22),
        (0.66, 0.78, 0.09),  # engine/proof
        (0.78, 0.88, 0.18),  # review
        (0.88, 0.95, 0.24),  # ecosystem
        (0.95, 1.0, 0.18),
    ]
    parts_dir = OUT / "music_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, (a, b, vol) in enumerate(bands):
        t0, t1 = a * total, b * total
        dur = max(0.05, t1 - t0)
        p = parts_dir / f"b{i}.wav"
        fade = min(0.7, dur * 0.12)
        run(
            [
                FFMPEG,
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(MUSIC_SRC),
                "-t",
                f"{dur:.3f}",
                "-af",
                f"aformat=sample_rates=44100:channel_layouts=stereo,volume={vol},"
                f"afade=t=in:d={fade:.2f},afade=t=out:st={max(0.05, dur - fade):.2f}:d={fade:.2f}",
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


def mux(video: Path, voice: Path, music: Path, out: Path) -> None:
    total = probe(video)
    filt = (
        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.1,"
        f"apad=whole_dur={total:.3f},asplit=2[vo_sc][vo_mix];"
        f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,"
        f"apad=whole_dur={total:.3f}[musride];"
        f"[musride][vo_sc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=320:makeup=1.3:mix=0.88[mus];"
        f"[vo_mix][mus]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
        f"alimiter=limit=0.94[a]"
    )
    tmp = out.with_suffix(".tmp.mp4")
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
        for n in names:
            shutil.copy2(src, base / n)
            print("copied", base / n)


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # persist new clips
    for name in (
        "sys_review_dashboard.mp4",
        "sys_employee_app.mp4",
        "sys_livemap_ops.mp4",
        "four_eyes_verify.mp4",
        "cameras_ai_ops.mp4",
        "comms_meetings.mp4",
        "payslip_review_send.mp4",
    ):
        try:
            src = find(name)
            dst = ROOT / name
            if src.resolve() != dst.resolve():
                shutil.copy2(src, dst)
        except FileNotFoundError:
            print("optional missing", name)

    raws = await synth_all_languages()
    durs = choose_durations(raws)
    (OUT / "durations.json").write_text(json.dumps(durs, indent=2), encoding="utf-8")
    print("durations", durs, "total", sum(durs.values()))

    visuals = []
    for bid in PLAN:
        dst = OUT / f"{bid}.mp4"
        print(f"visual {bid} {durs[bid]:.2f}s")
        build_visual(bid, durs[bid], dst)
        exact = OUT / f"{bid}_exact.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(dst),
                "-t",
                f"{durs[bid]:.3f}",
                "-vf",
                "fps=24,format=yuv420p,setsar=1",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "17",
                "-profile:v",
                "main",
                str(exact),
            ]
        )
        visuals.append(exact)

    silent = OUT / "video_silent.mp4"
    lst = OUT / "vlist.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in visuals), encoding="utf-8")
    run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "vlist.txt", "-c", "copy", "video_silent.mp4"],
        cwd=str(OUT),
    )

    music = OUT / "music_ride.wav"
    render_music_ride(probe(silent), music)

    for lang in ("de", "en", "ar"):
        lang_dir = VO_DIR / lang
        aligned = []
        for bid in PLAN:
            fit = lang_dir / f"{bid}_fit.wav"
            fit_audio(raws[lang][bid], fit, durs[bid])
            aligned.append(fit)
        voice = lang_dir / "voice_aligned.wav"
        alst = lang_dir / "alist.txt"
        alst.write_text("".join(f"file '{p.name}'\n" for p in aligned), encoding="utf-8")
        run(
            [
                FFMPEG,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                "alist.txt",
                "-c",
                "copy",
                "voice_aligned.wav",
            ],
            cwd=str(lang_dir),
        )
        out = OUT / f"SUPPIX_AI_ImageFilm_{lang.upper()}.mp4"
        print(f"mux {lang}")
        mux(silent, voice, music, out)
        names = [f"SUPPIX_AI_ImageFilm_{lang.upper()}.mp4"]
        if lang == "de":
            names += ["SUPPIX_AI_ImageFilm_PLAY.mp4", "SUPPIX_AI_ImageFilm_Synced.mp4"]
        publish(out, *names)
        print(lang, probe(out), out.stat().st_size)

    print("DONE")


if __name__ == "__main__":
    asyncio.run(main())
