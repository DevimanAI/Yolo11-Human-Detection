# Face recognition — register your face

## Important

This project does **not** train a face CNN from scratch. **DeepFace** ships with a pretrained model (**Facenet512**). You:

1. Add photos of yourself to a folder
2. DeepFace builds **embeddings** at startup
3. Live video crops are matched to your embeddings

Training a face model from zero would need datasets like VGGFace2 — out of scope here.

---

## Quick steps — recognize yourself

Replace `Iman` with your name.

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection

# 1. Install face dependencies (TensorFlow + DeepFace — large download)
.\.venv\Scripts\python.exe -m pip install -r requirements-face.txt

# 2. Create your folder
.\scripts\register_face.ps1 -Name "Iman"

# 3. Copy 2–3 clear, front-facing photos into:
#    data\known_faces\Iman\
#    e.g. front.jpg, side.jpg

# 4. Verify embeddings load
.\.venv\Scripts\python.exe scripts\build_face_gallery.py --build

# 5. Enable in .env (usually already true)
#    FACE_RECOGNITION_ENABLED=true
#    KNOWN_FACES_DIR=data/known_faces

# 6. Run demo — stand in front of webcam
.\.venv\Scripts\python.exe run.py
```

Facenet512 weights (~95 MB) download once to `.deepface/weights/` **inside this repo** (not `%USERPROFILE%`). Let the first run finish; interrupting leaves a broken partial file.

When your face is visible in the person box, the label should show **`Iman`** instead of `Unknown`.

---

## Photo tips

| Do | Avoid |
|----|--------|
| Front-facing, good light | Hat/sunglasses covering face |
| 1–3 photos per person | One tiny thumbnail |
| JPG or PNG | Heavy filters |
| Face fills a good part of the person crop | Standing very far from camera |

---

## Tune matching

In `.env`:

```ini
FACE_RECOGNITION_ENABLED=true
FACE_MODEL=Facenet512
FACE_MATCH_THRESHOLD=0.4
```

| Threshold | Effect |
|-----------|--------|
| Lower (0.35) | Easier match — more false names |
| Higher (0.45) | Stricter — more `Unknown` |

---

## Multiple people

```
data/known_faces/
  Iman/
    photo1.jpg
  Sara/
    photo1.jpg
```

Restart the server after adding folders.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Always `Unknown` | Lower threshold; use larger/closer face photos |
| `No module named 'deepface'` | `pip install -r requirements-face.txt` in `.venv` |
| Slow FPS | Set `FACE_RECOGNITION_ENABLED=false` for detection-only |
| Face layer off at startup | Check server log for DeepFace warning |

---

## How it works in code

1. YOLO detects **person** bbox  
2. Crop is sent to DeepFace `represent()`  
3. Cosine distance vs your stored embeddings  
4. Best match below threshold → your name on the bbox label  

See `app/face_registry.py` and `app/pipeline.py`.
