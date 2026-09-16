# YOLO Human Detection & Tracking

University-grade computer vision project: **Ultralytics YOLO** person detection, **ByteTrack/BoT-SORT** multi-object tracking, and optional **DeepFace** face recognition — with a **FastAPI** web preview for webcam or video files.

## Features

- Pre-trained YOLO (`yolo11n.pt`) — COCO class `person` (id 0)
- Persistent track IDs across frames (`bytetrack.yaml` or `botsort.yaml`)
- Optional face identification from `data/known_faces/<Name>/`
- Web UI with live MJPEG stream and source switching
- Windows-friendly setup documented for `C:\Users\Megam\source\repos\Yolo26-Human-Detection`

## Quick start (Windows)

```powershell
cd C:\Users\Megam\source\repos\Yolo26-Human-Detection
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
