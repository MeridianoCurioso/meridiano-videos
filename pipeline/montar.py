"""Uso: python3 montar.py <carpeta_video>  -> short.mp4 (1080x1920) con voz, clips, rótulos y subtítulos karaoke.
guion.json: titulo, hook (líneas separadas con \\N), voz, rate, escenas[{texto, rotulo, q, clip_id?}]"""
import json, subprocess, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); d=sys.argv[1]; os.chdir(d); g=json.load(open("guion.json")); n=len(g["escenas"])
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
PAD=0.15; os.makedirs("tmp",exist_ok=True)
durs=[dur(f"voz/{i:02d}.mp3")+PAD for i in range(n)]
starts=[sum(durs[:i]) for i in range(n)]; total=sum(durs)
# audio: each segment padded, concatenated
inp=[]; fl=""
for i in range(n): inp+=["-i",f"voz/{i:02d}.mp3"]; fl+=f"[{i}:a]aresample=44100,apad=whole_dur={durs[i]:.3f}[a{i}];"
fl+="".join(f"[a{i}]" for i in range(n))+f"concat=n={n}:v=0:a=1,loudnorm=I=-14:TP=-1.5[a]"
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",fl,"-map","[a]","-c:a","aac","-b:a","192k","tmp/audio.m4a"],check=True)
# video scenes
for i in range(n):
    D=durs[i]; src=f"assets/{i:02d}.mp4"; ss=min(1.0,max(0,dur(src)-D-0.1))
    vf=(f"scale=-2:1920:flags=lanczos,crop=1080:1920:x='(in_w-1080)/2+(t/{D:.3f}-0.5)*min(260\\,(in_w-1080)/2)':y=0,"
        f"eq=brightness=-0.04:saturation=1.12,fps=30,format=yuv420p")
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{ss}","-i",src,"-t",f"{D:.3f}","-an","-vf",vf,
        "-c:v","libx264","-preset","veryfast","-crf","18",f"tmp/s{i:02d}.mp4"],check=True); print("scene",i,flush=True)
open("tmp/list.txt","w").write("".join(f"file 's{i:02d}.mp4'\n" for i in range(n)))
# ASS subtitles
def t(s): h=int(s//3600); m=int(s%3600//60); return f"{h}:{m:02d}:{s%60:05.2f}"
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","",
"[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Sub,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,7,3,5,70,70,0,1",
"Style: Rotulo,Anton,78,&H00FFFFFF,&H00FFFFFF,&H001A1AC8,&H00000000,0,0,0,0,100,100,2,0,3,22,0,8,60,60,190,1",
"Style: Hook,Anton,118,&H0000E1FF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,8,4,8,60,60,330,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i,s in enumerate(g["escenas"]):
    a,b=starts[i],starts[i]+durs[i]
    if i==0: ass.append(f"Dialogue: 1,{t(a)},{t(b)},Hook,,0,0,0,,{{\\fad(150,0)\\t(0,250,\\fscx108\\fscy108)\\t(250,450,\\fscx100\\fscy100)}}"+g["hook"].upper())
    else: ass.append(f"Dialogue: 1,{t(a)},{t(b)},Rotulo,,0,0,0,,{{\\fad(120,0)\\fscx80\\fscy80\\t(0,180,\\fscx100\\fscy100)}}{s['rotulo']}")
    words=json.load(open(f"voz/{i:02d}.mp3.words.json"))
    chunks=[]; cur=[]
    for w in words:
        cur.append(w)
        if len(cur)==3 or w["w"][-1:] in ".,?!": chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
    flat=[(c,k) for c in chunks for k in range(len(c))]
    for j,(c,k) in enumerate(flat):
        ws=a+c[k]["s"]; we=a+(flat[j+1][0][flat[j+1][1]]["s"] if j+1<len(flat) else min(c[k]["e"]+0.4,durs[i]))
        txt=" ".join(("{\\c&H0000E1FF&\\fscx112\\fscy112}"+x["w"].upper()+"{\\r}") if m==k else x["w"].upper() for m,x in enumerate(c))
        ass.append(f"Dialogue: 0,{t(ws)},{t(we)},Sub,,0,0,0,,{{\\pos(540,1330)}}{txt}")
open("tmp/subs.ass","w").write("\n".join(ass)+"\n")
fd=os.path.join(HERE,"fonts")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","tmp/list.txt","-i","tmp/audio.m4a",
  "-vf",f"ass=tmp/subs.ass:fontsdir={fd}","-c:v","libx264","-preset","veryfast","-crf","20","-profile:v","high","-pix_fmt","yuv420p",
  "-c:a","copy","-shortest","-movflags","+faststart","short.mp4"],check=True)
print("total",round(total,2))
