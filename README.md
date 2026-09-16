# YOLO Human Detection & Tracking

University-grade computer vision project: **Ultralytics YOLO** person detection, **ByteTrack/BoT-SORT** multi-object tracking, and optional **DeepFace** face recognition — with a **FastAPI** web preview for webcam or video files.

## Features

- Pre-trained YOLO (`yolo11n.pt`) — COCO class `person` (id 0)
- Persistent track IDs across frames (`bytetrack.yaml` or `botsort.yaml`)
- Optional face identification from `data/known_faces/<Name>/`
- Web UI with live MJPEG stream and source switching
- Windows-friendly setup documented for `C:\Users\Megam\source\repos\Yolo11-Human-Detection`

## Get the project on your PC (from cloud)

The code lives in this Cursor cloud agent repo. On your Windows machine:

1. In the Cursor **agent view** for this project, click **Create repo** if you have not already (this publishes the code to your git remote).
2. Copy the clone URL shown there (Origin), or use:
   `https://origin.cursor.com/git/iman-ahmadi-dev/tmp-f3fe1242054da8a1.git`
3. In **PowerShell**:

```powershell
mkdir C:\Users\Megam\source\repos -Force
cd C:\Users\Megam\source\repos
git clone https://origin.cursor.com/git/iman-ahmadi-dev/tmp-f3fe1242054da8a1.git Yolo11-Human-Detection
cd Yolo11-Human-Detection
git checkout cursor/yolo-human-detection-d5be
```

Use the clone URL from **Create repo** once your permanent repository exists — it replaces the temporary URL above.

## Quick start (Windows)

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python scripts\smoke_test.py
python run.py
```

Open **http://127.0.0.1:8765** in your browser. Allow webcam access when prompted.

Full run/test guide: [docs/run-and-test.md](docs/run-and-test.md)  
Persian project article: [docs/project-article-fa.md](docs/project-article-fa.md)

## Quick start (Linux / cloud dev)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/smoke_test.py
python run.py
```

## Project layout

```
app/                  # FastAPI app, YOLO pipeline, face registry
  detector.py         # YOLO + tracking
  face_registry.py    # DeepFace embeddings
  pipeline.py         # Video capture + inference loop
  main.py             # Web server
data/
  known_faces/        # Register known people here
  sample/             # Smoke-test output
scripts/
  smoke_test.py       # Download sample + verify detection
requirements.txt
.env.example
run.py
```

## Configuration (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `YOLO_MODEL` | `yolo11n.pt` | Ultralytics weights |
| `TRACKER` | `bytetrack.yaml` | Tracker config |
| `VIDEO_SOURCE` | `0` | Webcam index or file path |
| `CONFIDENCE` | `0.5` | Detection threshold |
| `FACE_RECOGNITION_ENABLED` | `true` | Toggle face ID layer |
| `KNOWN_FACES_DIR` | `data/known_faces` | Known people photos |
| `PORT` | `8765` | Web server port |

## Register known faces

```
data/known_faces/
  Sara/
    front.jpg
  Ali/
    photo.png
```

Restart the server after adding images. Bounding boxes show `ID <track> | <name> (confidence)`.

## Limitations

- Face recognition runs on person crops; small or occluded faces may stay `Unknown`.
- First DeepFace run downloads model weights (~100 MB).
- GPU optional; CPU works for demo but lowers FPS.
- Single-client MJPEG stream; multiple tabs may compete for the same capture device.

## License

Educational use. Ultralytics YOLO and third-party libraries retain their own licenses.
