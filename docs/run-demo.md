# Run the web demo

## Prerequisites

- Python 3.10+ on PATH
- Use **`.venv`** (not Microsoft Store Python user-site — causes WinError 206 with PyTorch)

---

## Setup (once)

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
.\scripts\setup.ps1
copy .env.example .env
```

---

## Run

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe run.py
```

Browser: **http://127.0.0.1:8765**

---

## `.env` essentials

```ini
YOLO_MODEL=yolo11n.pt
TRACKER=bytetrack.yaml
VIDEO_SOURCE=0
CONFIDENCE=0.5
FACE_RECOGNITION_ENABLED=true
PORT=8765
```

| Variable | Meaning |
|----------|---------|
| `VIDEO_SOURCE=0` | Default webcam |
| `VIDEO_SOURCE=C:\path\video.mp4` | Video file |
| `YOLO_MODEL=runs/detect/.../best.pt` | After training |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: ultralytics` | Use `.\.venv\Scripts\python.exe`, run `setup.ps1` |
| Webcam blank | Close Zoom/Teams; try `VIDEO_SOURCE=1` |
| Port in use | Change `PORT=8766` |
| Face always Unknown | [face-recognition.md](face-recognition.md) |

---

## Linux / macOS

```bash
bash scripts/setup.sh
./.venv/bin/python scripts/smoke_test.py
./.venv/bin/python run.py
```
