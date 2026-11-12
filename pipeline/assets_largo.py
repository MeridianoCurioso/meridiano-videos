"""Uso: PIXABAY_API_KEY=... python3 assets_largo.py <carpeta>  -> assets/EE_K.mp4 (un clip por query; 'ids' en la escena fija clips)
Genera tmp/elegidos.jpg con todos los clips elegidos para revisarlos."""
import json, os, sys, io, urllib.parse
from common import get
from PIL import Image, ImageDraw
KEY = os.environ["PIXABAY_API_KEY"]; d = sys.argv[1]
g = json.load(open(f"{d}/guion.json")); os.makedirs(f"{d}/assets", exist_ok=True); os.makedirs(f"{d}/tmp", exist_ok=True)
def search(q): return json.loads(get(f"https://pixabay.com/api/videos/?key={KEY}&q={urllib.parse.quote(q)}&per_page=20&safesearch=true"))["hits"]
def by_id(i): return json.loads(get(f"https://pixabay.com/api/videos/?key={KEY}&id={i}"))["hits"][0]
def rend(h):
    vs = [v for v in h["videos"].values() if v.get("url") and v["width"] >= 1920]
    return min(vs, key=lambda v: v["width"]) if vs else h["videos"]["large"] if h["videos"]["large"]["url"] else h["videos"]["medium"]
used, cred, thumbs = set(), [], []
for i, s in enumerate(g["escenas"]):
    ids = s.get("ids") or [None]*len(s["q"])
    for k, q in enumerate(s["q"]):
        out = f"{d}/assets/{i:02d}_{k}.mp4"
        if ids[k]: h = by_id(ids[k])
        else:
            hits = [x for x in search(q) if x["id"] not in used and x["duration"] >= 6]
            if not hits: hits = [x for x in search(q.split()[0]) if x["id"] not in used]
            h = hits[0]
        used.add(h["id"]); r = rend(h)
        idf = out[:-4] + ".id"
        if not (os.path.exists(out) and os.path.exists(idf) and open(idf).read() == str(h["id"])):
            open(out, "wb").write(get(r["url"], 300)); open(idf, "w").write(str(h["id"]))
        cred.append(f"{i:02d}_{k} {h['pageURL']} {r['width']}x{r['height']}")
        t = h["videos"]["large"]["thumbnail"] or h["videos"]["medium"]["thumbnail"]
        thumbs.append((f"{i}.{k} {s.get('rotulo','')[:12]} {h['id']}", Image.open(io.BytesIO(get(t))).convert("RGB").resize((320, 180))))
        print(cred[-1], flush=True)
open(f"{d}/assets/creditos.txt", "w").write("\n".join(cred))
cols = 6; rows = (len(thumbs)+cols-1)//cols; sh = Image.new("RGB", (320*cols, 180*rows))
for n, (lab, im) in enumerate(thumbs):
    sh.paste(im, ((n % cols)*320, (n//cols)*180)); ImageDraw.Draw(sh).text(((n % cols)*320+6, (n//cols)*180+6), lab, fill="yellow")
sh.save(f"{d}/tmp/elegidos.jpg"); print("tmp/elegidos.jpg")
