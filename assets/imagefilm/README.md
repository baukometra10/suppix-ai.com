# SUPPIX AI ImageFilm

## Masters (Desktop\Videos)

- `SUPPIX_AI_ImageFilm_DE.mp4` / `_EN.mp4` / `_AR.mp4` (~3:16, full quality)
- `SUPPIX_AI_AD_25s_DE.mp4` / `_EN.mp4` / `_AR.mp4` (ad cuts)

## Website (web-optimized 720p)

Under `assets/imagefilm/web/`:

| File | Use |
|---|---|
| `SUPPIX_AI_ImageFilm_*.mp4` (~42 MB) | Main product video by language |
| `SUPPIX_AI_AD_25s_*.mp4` (~12 MB) | Hero short clip |
| `imagefilm-poster.jpg` | Poster |

Wired via `site-config.js` → `demoVideoByLang` + `shortVideoByLang`.  
Lohn-bridge videos remain in the WorkPass Lohn section only.

## Rebuild web compressions

```bash
python assets/imagefilm/make_web_versions.py
```
