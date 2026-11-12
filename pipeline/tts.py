"""Uso: python3 tts.py <carpeta_video>  -> genera voz/NN.mp3 + NN.mp3.words.json por escena (con reintentos)."""
import asyncio, json, os, sys, time
import edge_tts, edge_tts.communicate as c
from common import ssl_ctx
c._SSL_CTX = ssl_ctx()
async def one(text, voice, out, rate):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(out, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "s": ch["offset"]/1e7, "e": (ch["offset"]+ch["duration"])/1e7})
    json.dump(words, open(out + ".words.json", "w"), ensure_ascii=False)
d = sys.argv[1]; g = json.load(open(f"{d}/guion.json")); os.makedirs(f"{d}/voz", exist_ok=True)
for i, s in enumerate(g["escenas"]):
    for intento in range(5):
        try:
            asyncio.run(one(s["texto"], g.get("voz", "it-IT-GiuseppeMultilingualNeural"), f"{d}/voz/{i:02d}.mp3", g.get("rate", "+10%"))); break
        except Exception as e:
            print("reintento", i, e); time.sleep(3 + intento * 2)
    else: sys.exit(f"TTS falló en escena {i}")
    print("voz", i, "ok")
