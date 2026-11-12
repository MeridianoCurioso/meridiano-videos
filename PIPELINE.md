# Meridiano Curioso: procedimiento diario

Canal: **Meridiano Curioso** (@meridianocurioso, ID `UC9iWZCq6bw80TX8L2F56EIA`).
Nicho: curiosidades de historia y geografía, en español, para toda la audiencia hispanohablante.
Formato: Short vertical 1080x1920, de 40 a 58 s.
Voz: `it-IT-GiuseppeMultilingualNeural` a +10 % (la "voz 10" elegida por el dueño).

## 1. Preparar el entorno
```bash
pip install --break-system-packages -q edge-tts
git clone --depth 1 https://github.com/MeridianoCurioso/meridiano-videos /home/claude/meridiano-videos
```
También hacen falta ffmpeg (con libass), Pillow y la variable de entorno `PIXABAY_API_KEY`.

## 2. Investigar (1 sola llamada a vidIQ: el plan da 150 créditos al mes y cada llamada cuesta 5)
- Usa `vidiq_trending_videos` con videoFormat=short, videoTitleLanguage=es, sortBy=vph y publicados en los últimos 7 días. En titleQuery pon un tema del nicho y ve rotándolo: curiosidades historia, geografía, países, mapas, sabías que, imperios, ciudades, idiomas…
- Busca los vídeos de **canales pequeños con muchas vistas**, porque señalan una fórmula que funciona por sí sola. Adapta la fórmula a un tema **nuevo**; no copies el vídeo.
- Revisa `historial.md` y no repitas ningún tema.

## 3. Guion: crea la carpeta `dias/AAAA-MM-DD_slug/guion.json`
```json
{"titulo": "… #shorts (máximo 100 caracteres)",
 "hook": "LÍNEA 1\\NLÍNEA 2\\NLÍNEA 3",
 "voz": "it-IT-GiuseppeMultilingualNeural", "rate": "+10%",
 "descripcion": "2 líneas + hashtags + 'Vídeos: Pixabay.'",
 "tags": ["…"],
 "escenas": [{"texto": "lo que dice la voz", "rotulo": "1. NOMBRE", "q": "pixabay query in english"}]}
```
- Entre 8 y 11 escenas, unas 130 palabras en total. La escena 0 es el gancho y debe prometer algo ("y el tercero te va a sorprender"); la última es la pregunta para comentarios.
- **Exactitud ante todo:** usa solo datos que puedas verificar. Si dudas de uno, búscalo en la web o quítalo. Los números van escritos en letra en el texto de la voz.

## 4. Voz, clips, montaje y revisión
```bash
cd dias/AAAA-MM-DD_slug
P=/home/claude/meridiano-videos/pipeline
python3 $P/assets.py . --cands      # genera tmp/cands.jpg: MÍRALO
```
Para cada escena, elige el clip que muestre de verdad ese lugar o esa cosa (descarta paisajes de otro país, vallas, mapas equivocados…) y ponlo en `clip_id` dentro de guion.json. Después:
```bash
python3 $P/tts.py . && python3 $P/assets.py . && python3 $P/montar.py . && python3 $P/revisar.py .
```
Mira `tmp/revision.jpg`: los rótulos y subtítulos tienen que leerse bien y los clips encajar con el texto. El vídeo debe durar menos de 60 s.

## 5. Subir
1. Copia `short.mp4` a `videos/AAAA-MM-DD_slug.mp4` y añade el tema a `historial.md`. Solo se suben `videos/` e `historial.md`; nunca `dias/*/assets` (pesan demasiado).
2. Haz `git add videos historial.md && git commit && git push`.
3. Llama a `vidiq_video_upload` con url = `https://raw.githubusercontent.com/MeridianoCurioso/meridiano-videos/main/videos/<archivo>.mp4`.
4. Crea el borrador con `vidiq_social_post_draft_create` (YOUTUBE, platformAccountId `UC9iWZCq6bw80TX8L2F56EIA`, categoryId 27 y el modo de publicación que indique la tarea) y publícalo con `vidiq_social_post_publish`.
5. Comprueba el resultado con `vidiq_social_post_status` hasta obtener el postUrl.
