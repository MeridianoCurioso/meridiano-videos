"""Uso: PIXABAY_API_KEY=... python3 assets.py <carpeta_video> [--cands]
Descarga un clip de Pixabay por escena (campo q; o clip_id si está fijado).
--cands: solo genera tmp/cands.jpg con 5 candidatos por escena para elegir clip_id a ojo."""
import json, os, sys, io, urllib.parse
from common import get
KEY = os.environ["PIXABAY_API_KEY"]
d = sys.argv[1]; g = json.load(open(f"{d}/guion.json")); os.makedirs(f"{d}/assets", exist_ok=True); os.makedirs(f"{d}/tmp", exist_ok=True)
def search(q, n=10): return json.loads(get(f"https://pixabay.com/api/videos/?key={KEY}&q={urllib.parse.quote(q)}&per_page={n}&safesearch=true"))["hits"]
def by_id(i): return json.loads(get(f"https://pixabay.com/api/videos/?key={KEY}&id={i}"))["hits"][0]
if "--cands" in sys.argv:
    from PIL import Image, ImageDraw
    W, H = 320, 180; rows = g["escenas"]; sheet = Image.new("RGB", (W*5, H*len(rows)))
    for r, s in enumerate(rows):
        for c, h in enumerate([x for x in search(s["q"]) if x["duration"] >= 5][:5]):
            v = h["videos"]; t = v["large"]["thumbnail"] or v["medium"]["thumbnail"]
            sheet.paste(Image.open(io.BytesIO(get(t))).convert("RGB").resize((W, H)), (c*W, r*H))
            ImageDraw.Draw(sheet).text((c*W+6, r*H+6), f"esc{r} id={h['id']}", fill="yellow")
    sheet.save(f"{d}/tmp/cands.jpg"); print("tmp/cands.jpg listo"); sys.exit()
used, credits = set(), []
for i, s in enumerate(g["escenas"]):
    if s.get("clip_id"): h = by_id(s["clip_id"])
    else: h = [x for x in search(s["q"], 20) if x["id"] not in used and x["duration"] >= 5][0]
    used.add(h["id"]); v = h["videos"]; r = v["large"] if v["large"]["url"] else v["medium"]
    open(f"{d}/assets/{i:02d}.mp4", "wb").write(get(r["url"], 300))
    credits.append(f"{i:02d} {h['pageURL']} {r['width']}x{r['height']}"); print(credits[-1], flush=True)
open(f"{d}/assets/creditos.txt", "w").write("\n".join(credits))
