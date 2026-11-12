"""Uso: python3 montar_largo.py <carpeta>  -> largo.mp4 (1920x1080). Necesita voz/NN.mp3 (tts.py) y assets/EE_K.mp4 (assets_largo.py)."""
import json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); d = sys.argv[1]; os.chdir(d)
g = json.load(open("guion.json")); n = len(g["escenas"]); os.makedirs("tmp", exist_ok=True)
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
PAD = 0.7
durs = [dur(f"voz/{i:02d}.mp3") + PAD for i in range(n)]; starts = [sum(durs[:i]) for i in range(n)]; total = sum(durs)
inp, fl = [], ""
for i in range(n): inp += ["-i", f"voz/{i:02d}.mp3"]; fl += f"[{i}:a]aresample=44100,apad=whole_dur={durs[i]:.3f}[a{i}];"
fl += "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,loudnorm=I=-14:TP=-1.5[a]"
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",fl,"-map","[a]","-c:a","aac","-b:a","192k","tmp/audio.m4a"], check=True)
parts = []
for i, s in enumerate(g["escenas"]):
    k_n = len(s["q"]); seg = durs[i] / k_n
    for k in range(k_n):
        src = f"assets/{i:02d}_{k}.mp4"; sd = dur(src); ss = max(0, min(1.0, sd - seg - 0.1)); out = f"tmp/p{i:02d}_{k}.mp4"
        # si el clip es más corto que el tramo, se ralentiza un poco
        slow = max(1.0, (seg + 0.2) / max(0.5, sd - ss))
        dirn = 1 if (i + k) % 2 == 0 else -1
        vf = (f"setpts={slow:.3f}*PTS,scale=2112:1188:force_original_aspect_ratio=increase:flags=lanczos,crop=2112:1188,"
              f"crop=1920:1080:x='96+{dirn}*96*(2*t/{seg:.3f}-1)':y='54+40*(t/{seg:.3f}-0.5)',"
              f"eq=saturation=1.08:contrast=1.03,fps=30,format=yuv420p")
        if "--reuse" in sys.argv and os.path.exists(out): parts.append(out); continue
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{ss}","-i",src,"-t",f"{seg:.3f}","-an","-vf",vf,
                        "-c:v","libx264","-preset","veryfast","-crf","19",out], check=True)
        parts.append(out)
    print("escena", i, flush=True)
open("tmp/list.txt","w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
def t(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
NAVY, CREAM, GOLD, RED = "&H005F3A1F", "&H00D2E9F3", "&H0027A2C9", "&H002F45B5"
ass = ["[Script Info]","ScriptType: v4.00+","PlayResX: 1920","PlayResY: 1080","WrapStyle: 0","",
"[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
f"Style: Sub,DM Serif Display,54,&H00FFFFFF,&H00FFFFFF,&H00151515,&H80000000,0,0,0,0,100,100,0.5,0,1,3.2,1.5,2,160,160,58,1",
f"Style: Pais,DM Serif Display,74,{NAVY},{NAVY},{CREAM},&H00000000,0,0,0,0,100,100,2,0,3,26,0,7,90,90,90,1",
f"Style: Num,DM Serif Display,40,{RED},{RED},{CREAM},&H00000000,0,1,0,0,100,100,1,0,3,14,0,7,90,90,60,1",
f"Style: Titulo,DM Serif Display,96,{NAVY},{NAVY},{CREAM},&H00000000,0,0,0,0,100,100,1,0,3,34,0,5,120,120,0,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
paises = [i for i, s in enumerate(g["escenas"]) if s.get("rotulo") and not s["rotulo"].upper().startswith("BONUS")]
ass.append(f"Dialogue: 2,{t(0.3)},{t(min(5.5, durs[0]))},Titulo,,0,0,0,,{{\\fad(400,400)}}" + g.get("titulo_pantalla", g["titulo"].split("?")[0] + "?"))
for i, s in enumerate(g["escenas"]):
    a = starts[i]
    if s.get("rotulo"):
        e = a + min(5.0, durs[i] - 0.3)
        if i in paises: ass.append(f"Dialogue: 2,{t(a+0.2)},{t(e)},Num,,0,0,0,,{{\\fad(250,250)\\move(40,60,90,60,0,350)}}{paises.index(i)+1} de {len(paises)}")
        ass.append(f"Dialogue: 2,{t(a+0.2)},{t(e)},Pais,,0,0,0,,{{\\fad(250,250)\\move(40,128,90,128,0,350)}}{s['rotulo']}")
    words = json.load(open(f"voz/{i:02d}.mp3.words.json")); chunks, cur = [], []
    toks = s["texto"].split()
    if len(toks) == len(words):   # recupera puntuación y mayúsculas del texto original
        for w, tk in zip(words, toks): w["w"] = tk
    for w in words:
        cur.append(w)
        if len(cur) >= 8 or w["w"][-1:] in ".?!" or (w["w"][-1:] in ",:" and len(cur) >= 3): chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for j, c in enumerate(chunks):
        cs = a + c[0]["s"]; ce = a + (chunks[j+1][0]["s"] if j + 1 < len(chunks) else min(c[-1]["e"] + 0.5, durs[i]))
        ass.append(f"Dialogue: 0,{t(cs)},{t(ce)},Sub,,0,0,0,,{' '.join(x['w'] for x in c)}")
open("tmp/subs.ass","w").write("\n".join(ass) + "\n")
fd = os.path.join(HERE, "fonts"); wm = os.path.join(HERE, "marca", "marca_agua.png")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","tmp/list.txt","-i","tmp/audio.m4a","-i",wm,
  "-filter_complex",f"[0:v][2:v]overlay=W-w-40:40:format=auto,ass=tmp/subs.ass:fontsdir={fd}[v]","-map","[v]","-map","1:a",
  "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","copy","-shortest","-movflags","+faststart","largo.mp4"], check=True)
print("total", round(total, 1), "s")
