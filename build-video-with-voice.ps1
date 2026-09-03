$ffmpeg = "C:\Users\u4363\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
$input = "c:\Users\u4363\Desktop\Screenshots\Recording 2026-05-22 222913.mp4"
$music = "c:\Users\u4363\Desktop\Baukometra\assets\bg-music-soft.wav"
$voiceText = "c:\Users\u4363\Desktop\Baukometra\assets\voiceover-text.txt"
$voiceRaw = "c:\Users\u4363\Desktop\Baukometra\assets\voiceover-raw.mp3"
$mixedAudio = "c:\Users\u4363\Desktop\Baukometra\assets\demo-voice-music.m4a"
$raw = "c:\Users\u4363\Desktop\Baukometra\assets\WORKPASS-v4-raw.mp4"
$final = "c:\Users\u4363\Desktop\Baukometra\assets\WORKPASS-demo-v4.mp4"

Write-Host "1/4 KI-Stimme (de-DE-KatjaNeural)..."
edge-tts --voice de-DE-KatjaNeural --rate="-3%" --file $voiceText --write-media $voiceRaw
if ($LASTEXITCODE -ne 0) { throw "TTS fehlgeschlagen" }

Write-Host "2/4 Stimme + Musik mischen..."
& $ffmpeg -y -hide_banner -loglevel error -i $voiceRaw -i $music `
  -filter_complex "[0:a]adelay=1500|1500,volume=1.2[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=longest" `
  -c:a aac -b:a 192k -t 115.73 $mixedAudio
if ($LASTEXITCODE -ne 0) { throw "Audio-Mix fehlgeschlagen" }

Write-Host "3/4 Video encodieren..."
& $ffmpeg -y -hide_banner -loglevel error -i $input -i $mixedAudio `
  -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0f1419,fade=t=in:st=0:d=1.5[v]" `
  -map "[v]" -map 1:a -c:v libx264 -profile:v main -pix_fmt yuv420p -preset ultrafast -crf 22 -c:a copy -shortest $raw
if ($LASTEXITCODE -ne 0) { throw "Video-Encode fehlgeschlagen" }

Write-Host "4/4 Browser-Optimierung..."
& $ffmpeg -y -hide_banner -loglevel error -i $raw -c copy -movflags +faststart $final
& $ffmpeg -v error -i $final -f null -
if ($LASTEXITCODE -ne 0) { throw "Validierung fehlgeschlagen" }

Copy-Item -Force $final "c:\Users\u4363\Desktop\Baukometra\assets\WORKPASS-demo.mp4"
Copy-Item -Force $final "c:\Users\u4363\Desktop\Baukometra\assets\demo-video.mp4"
Remove-Item $raw -Force -ErrorAction SilentlyContinue
Write-Host "FERTIG: $final"
