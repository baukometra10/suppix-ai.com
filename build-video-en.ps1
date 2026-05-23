$ffmpeg = "C:\Users\u4363\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
$input = "c:\Users\u4363\Desktop\Screenshots\Recording 2026-05-22 222913.mp4"
$music = "c:\Users\u4363\Desktop\test-folder\assets\bg-music-soft.wav"
$voiceText = "c:\Users\u4363\Desktop\test-folder\assets\voiceover-text-en.txt"
$wav = "c:\Users\u4363\Desktop\test-folder\assets\voiceover-en-raw.wav"
$audio = "c:\Users\u4363\Desktop\test-folder\assets\demo-voice-music-en.m4a"
$final = "c:\Users\u4363\Desktop\test-folder\assets\baupass-demo-en.mp4"

Write-Host "1/3 English voice (Windows SAPI)..."
$text = Get-Content $voiceText -Raw
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$enVoice = $synth.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like "en-*" } | Select-Object -First 1
if ($enVoice) { $synth.SelectVoice($enVoice.VoiceInfo.Name) }
$synth.SetOutputToWaveFile($wav)
$synth.Speak($text.Trim())
$synth.Dispose()

Write-Host "2/3 Mix audio..."
& $ffmpeg -y -hide_banner -loglevel error -i $wav -i $music -filter_complex "[0:a]adelay=1500|1500,volume=1.1[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=longest" -c:a aac -b:a 192k -t 115.73 $audio

Write-Host "3/3 Render video..."
& $ffmpeg -y -hide_banner -loglevel error -i $input -i $audio -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0f1419,fade=t=in:st=0:d=1.5[v]" -map "[v]" -map 1:a -c:v libx264 -profile:v main -pix_fmt yuv420p -preset ultrafast -crf 22 -c:a copy -shortest $final
& $ffmpeg -v error -i $final -f null -
Write-Host "FERTIG: $final"
