# YOLO11 Human Detection & Tracking

Person detection (YOLO11), multi-object tracking (ByteTrack), optional face ID (DeepFace), and a FastAPI web demo.

## Documentation

**Start here:** [docs/README.md](docs/README.md)

| Guide | Purpose |
|-------|---------|
| [docs/run-demo.md](docs/run-demo.md) | Install and run the webcam demo |
| [docs/train-yolo.md](docs/train-yolo.md) | Fine-tune YOLO11 (2000+500 images) |
| [docs/face-recognition.md](docs/face-recognition.md) | Register your face for recognition |
| [docs/training-reference.md](docs/training-reference.md) | Hyperparameters & architecture (optional) |
| [docs/thesis/](docs/thesis/) | Persian thesis draft |

---

## Quick start — demo

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe run.py
```

http://127.0.0.1:8765

Always use `.\.venv\Scripts\python.exe` — not bare `python` (Store Python breaks PyTorch on Windows).

---

## Quick start — train YOLO11

```powershell
.\scripts\setup-train.ps1
.\scripts\download_dataset.ps1
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py
.\scripts\train_yolo11.ps1
```

Convert keeps **2000 train + 500 val** images (see [docs/train-yolo.md](docs/train-yolo.md)).

---

## Quick start — recognize your face

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-face.txt
.\scripts\register_face.ps1 -Name "YourName"
# add photos to data\known_faces\YourName\
.\.venv\Scripts\python.exe scripts\build_face_gallery.py --build
.\.venv\Scripts\python.exe run.py
```

DeepFace uses a **pretrained** model — you add photos, not train a CNN. Details: [docs/face-recognition.md](docs/face-recognition.md).

---

## `.env` (common)

```ini
YOLO_MODEL=yolo11n.pt
TRACKER=bytetrack.yaml
VIDEO_SOURCE=0
CONFIDENCE=0.5
FACE_RECOGNITION_ENABLED=true
KNOWN_FACES_DIR=data/known_faces
PORT=8765
```

After training: `YOLO_MODEL=runs/detect/person_yolo11n/weights/best.pt`
