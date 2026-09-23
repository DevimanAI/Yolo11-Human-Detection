# YOLO Human Detection & Tracking

University-grade computer vision project: **Ultralytics YOLO** person detection, **ByteTrack/BoT-SORT** multi-object tracking, and optional **DeepFace** face recognition — with a **FastAPI** web preview for webcam or video files.

## Features

- Pre-trained YOLO (`yolo11n.pt`) — COCO class `person` (id 0)
- Persistent track IDs across frames (`bytetrack.yaml` or `botsort.yaml`)
- Optional face identification from `data/known_faces/<Name>/`
- Web UI with live MJPEG stream and source switching

## Quick start (Windows)

Python 3.10+ must be on PATH (`python --version`). The `py` launcher is **not** required.

Use a **project virtual environment**. Installing into Microsoft Store Python fails on Windows with **WinError 206** (path too long) while upgrading PyTorch, so `ultralytics` never gets installed.

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
.\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe run.py
```

`setup.ps1` creates `.venv`, installs `requirements.txt`, and copies `.env.example` to `.env` if needed.

Open **http://127.0.0.1:8765** in your browser. Allow webcam access when prompted.

Equivalent manual steps (if you prefer not to run the script):

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe run.py
```

If `Activate.ps1` is blocked by execution policy, keep using `.\.venv\Scripts\python.exe` as above — you do not need to activate the venv.

Optional face recognition (heavy: TensorFlow + DeepFace):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-face.txt
```

Full run/test guide: [docs/run-and-test.md](docs/run-and-test.md)  
Persian project article: [docs/project-article-fa.md](docs/project-article-fa.md)

## Training (fine-tune YOLO11 on person data)

The app ships with **pretrained** `yolo11n.pt` (COCO). To train on a person dataset (CrowdHuman — **not** the unrelated [CASIA tampering dataset](https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset)):

```powershell
.\scripts\setup-train.ps1
.\scripts\download_dataset.ps1
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py
.\scripts\train_yolo11.ps1
```

Smoke pipeline only (no Kaggle): `convert_crowdhuman.py --mini` then `train_yolo11.ps1 -Epochs 3`

| Doc | Purpose |
|-----|---------|
| [docs/training-guide.md](docs/training-guide.md) | Step-by-step runbook |
| [docs/training-params-defense-fa.md](docs/training-params-defense-fa.md) | Persian defense Q&A (hyperparams, anchors, CNN) |
| [docs/deepface-gallery-fa.md](docs/deepface-gallery-fa.md) | Face gallery setup |
| [docs/thesis/](docs/thesis/) | ~40-page Persian thesis draft |

### Model specification (inference app)

| Item | Value |
|------|-------|
| Architecture | YOLO11n (Ultralytics), **anchor-free** Detect head |
| Pretrained weights | `yolo11n.pt` — COCO, class `person` = id 0 |
| Input (train default) | 640×640 |
| Params | ~2.6M (nano) |
| Tracking | ByteTrack / BoT-SORT (not part of detector training) |
| Face ID | DeepFace Facenet512 — pretrained gallery (optional) |

## Quick start (Linux / macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python scripts/smoke_test.py
python run.py
```

Or: `bash scripts/setup.sh`

## Clone

```powershell
git clone https://github.com/DevimanAI/Yolo11-Human-Detection.git
cd Yolo11-Human-Detection
```

## Project layout

```
app/                  # FastAPI app, YOLO pipeline, face registry
  detector.py         # YOLO + tracking
  face_registry.py    # DeepFace embeddings (optional)
  pipeline.py         # Video capture + inference loop
  main.py             # Web server
  env_check.py        # Missing-package hints for smoke/run
data/
  known_faces/        # Register known people here
  sample/             # Smoke-test output
scripts/
  setup.ps1           # Windows venv + pip install
  setup-train.ps1     # Training deps + GPU check
  download_dataset.ps1
  convert_crowdhuman.py
  train_yolo11.ps1
  export_metrics.py
  build_face_gallery.py
  smoke_test.py       # Download sample + verify detection
configs/
  person_crowdhuman.yaml
  train_yolo11n.yaml
requirements.txt      # Core demo (no TensorFlow)
requirements-train.txt
requirements-face.txt # Optional DeepFace extras
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

Face labels stay `Unknown` until `requirements-face.txt` is installed and photos exist under `known_faces`.

## Register known faces

```
data/known_faces/
  Sara/
    front.jpg
  Ali/
    photo.png
```

Restart the server after adding images. Bounding boxes show `ID <track> | <name> (confidence)`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `py` is not recognized | Use `python -m venv .venv` (or `.\scripts\setup.ps1`) |
| `Activate.ps1` is not recognized | The venv was not created. Run setup, then `.\.venv\Scripts\python.exe` |
| `ModuleNotFoundError: ultralytics` | Packages went to Store Python. Reinstall **inside** `.venv` |
| `WinError 206` filename too long | Stop using Store Python user-site. Use `.venv` (shorter path) |
| Smoke test finds 0 people | Confirm `data/sample/bus.jpg` downloaded; retry on a working network |

## Limitations

- Face recognition runs on person crops; small or occluded faces may stay `Unknown`.
- First DeepFace run downloads model weights (~100 MB).
- GPU optional; CPU works for demo but lowers FPS.
- Single-client MJPEG stream; multiple tabs may compete for the same capture device.

## License

Educational use. Ultralytics YOLO and third-party libraries retain their own licenses.
