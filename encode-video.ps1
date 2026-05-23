$ffmpeg = "C:\Users\u4363\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
$input = "c:\Users\u4363\Desktop\Screenshots\Recording 2026-05-22 222913.mp4"
$music = "c:\Users\u4363\Desktop\test-folder\assets\bg-music.wav"
$raw = "c:\Users\u4363\Desktop\test-folder\assets\demo-video-raw.mp4"
$final = "c:\Users\u4363\Desktop\test-folder\assets\demo-video.mp4"

Write-Host "Step 1/2: Video + Musik encodieren..."
& $ffmpeg -y -hide_banner -loglevel error -stats -i $input -i $music `
  -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0f1419,fade=t=in:st=0:d=1.5[v];[1:a]volume=0.4,afade=t=in:st=0:d=3,afade=t=out:st=111:d=4[music];[0:a]volume=0.75[orig];[orig][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" `
  -map "[v]" -map "[aout]" -c:v libx264 -profile:v main -pix_fmt yuv420p -preset ultrafast -crf 22 -c:a aac -b:a 192k $raw

if ($LASTEXITCODE -ne 0) { Write-Error "Encode fehlgeschlagen"; exit 1 }

Write-Host "Step 2/2: Fuer Browser optimieren..."
& $ffmpeg -y -hide_banner -loglevel error -i $raw -c copy -movflags +faststart $final

if ($LASTEXITCODE -ne 0) { Write-Error "Optimierung fehlgeschlagen"; exit 1 }

& $ffmpeg -v error -i $final -f null -
if ($LASTEXITCODE -ne 0) { Write-Error "Validierung fehlgeschlagen"; exit 1 }

Remove-Item $raw -Force -ErrorAction SilentlyContinue
Write-Host "FERTIG: $final ($((Get-Item $final).Length) bytes)"
