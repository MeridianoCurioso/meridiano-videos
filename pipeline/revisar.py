"""Uso: python3 revisar.py <carpeta_video>  -> tmp/revision.jpg con 8 fotogramas del short.mp4 + duración y volumen."""
import subprocess, sys, os
from PIL import Image
d = sys.argv[1]; f = f"{d}/short.mp4"
D = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
ts = [0.5 + k*(D-1)/7 for k in range(8)]; sheet = Image.new("RGB", (270*8, 480))
for k, t in enumerate(ts):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t:.2f}","-i",f,"-frames:v","1","-vf","scale=270:480",f"{d}/tmp/r{k}.jpg"], check=True)
    sheet.paste(Image.open(f"{d}/tmp/r{k}.jpg"), (k*270, 0))
sheet.save(f"{d}/tmp/revision.jpg")
lufs = subprocess.run(["ffmpeg","-i",f,"-af","ebur128","-f","null","-"], capture_output=True, text=True).stderr.split("Integrated loudness:")[-1].split("LUFS")[0].strip()
print(f"duración {D:.1f}s | {lufs} LUFS | tmp/revision.jpg")
