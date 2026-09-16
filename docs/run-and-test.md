# Run and Test Guide — YOLO Human Detection & Tracking

This guide explains how to set up, run, and verify the project on **Windows** at:

`C:\Users\Megam\source\repos\Yolo26-Human-Detection`

The same steps work on Linux/macOS with path and shell adjustments.

---

## 1. Prerequisites

| Requirement | Version / notes |
|-------------|-----------------|
| Python | 3.10 or newer (3.11 recommended on Windows) |
| Git | To clone the repository |
| Webcam | Optional; required for live demo |
| GPU | Optional; CUDA speeds up YOLO and DeepFace |

### Windows-specific

1. Install Python from [python.org](https://www.python.org/downloads/) and check **“Add Python to PATH”**.
2. Open **PowerShell** (not CMD) for the commands below.
3. Allow the app through Windows Firewall when prompted (port **8765**).

---

## 2. Clone and enter the project

```powershell
cd C:\Users\Megam\source\repos
git clone <your-repo-url> Yolo26-Human-Detection
cd Yolo26-Human-Detection
```

If you already have the folder, pull the latest branch:

```powershell
cd C:\Users\Megam\source\repos\Yolo26-Human-Detection
git pull
git checkout cursor/yolo-human-detection-d5be
```

---

## 3. Create virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

---

## 4. Install dependencies

```powershell
pip install -r requirements.txt
```

**First run notes:**

- Ultralytics downloads `yolo11n.pt` automatically (~5 MB).
- DeepFace downloads face model weights on first face recognition use (~100 MB).
- Installation may take 5–15 minutes on Windows depending on network and CPU.

---

## 5. Configure environment

```powershell
copy .env.example .env
notepad .env
```

Common settings:

```ini
YOLO_MODEL=yolo11n.pt
TRACKER=bytetrack.yaml
VIDEO_SOURCE=0
CONFIDENCE=0.5
FACE_RECOGNITION_ENABLED=true
KNOWN_FACES_DIR=data/known_faces
HOST=127.0.0.1
PORT=8765
```

### Video file instead of webcam

```ini
VIDEO_SOURCE=C:\Users\Megam\Videos\campus.mp4
```

Use forward slashes if backslashes cause issues:

```ini
VIDEO_SOURCE=C:/Users/Megam/Videos/campus.mp4
```

---

## 6. Smoke test (no webcam required)

Verifies YOLO download, person detection, and sample output:

```powershell
python scripts\smoke_test.py
```

**Expected output:**

- Downloads `data\sample\bus.jpg` if missing.
- Prints `Detected N person(s)` with bounding boxes.
- Saves `data\sample\bus_detected.jpg`.

Open the annotated image to confirm green boxes around people.

**Success criteria:** at least one person detected on the bus sample (typically 3–4).

---

## 7. Register known faces (optional)

1. Create a folder per person under `data\known_faces\`.
2. Add 1–3 clear front-facing photos (`.jpg`, `.png`).

Example:

```
data\known_faces\
  Sara\
    front.jpg
  Ali\
    photo1.jpg
    photo2.jpg
```

3. Restart the server after adding photos.
4. When a tracked person’s face matches, the label changes from `Unknown` to the folder name.

Tune matching in `.env`:

```ini
FACE_MATCH_THRESHOLD=0.4
```

Lower = stricter matching.

---

## 8. Start the web demo

```powershell
python run.py
```

Open in a browser:

**http://127.0.0.1:8765**

### UI features

- Live MJPEG stream with bounding boxes and track IDs.
- Stats: FPS, person count, face recognition on/off.
- **Source** field: change webcam index (`0`, `1`, …) or paste a video path, then **Apply**.

### API checks

Status JSON:

```powershell
curl http://127.0.0.1:8765/api/status
```

Change source via API:

```powershell
curl -X POST http://127.0.0.1:8765/api/source `
  -H "Content-Type: application/json" `
  -d "{\"source\": \"0\"}"
```

---

## 9. Test matrix

| Test | Steps | Pass criteria |
|------|--------|---------------|
| Dependency install | `pip install -r requirements.txt` | No errors |
| Model download | `python scripts\smoke_test.py` | `yolo11n.pt` present, persons detected |
| Web server | `python run.py` | Page loads at port 8765 |
| Webcam | Default `VIDEO_SOURCE=0` | Stream shows live video with boxes |
| Video file | Set path in UI or `.env` | File plays with tracking IDs stable across frames |
| Face ID | Add photos under `known_faces` | Known person labeled by name |
| Tracker swap | `TRACKER=botsort.yaml` in `.env` | Tracking still works after restart |

---

## 10. Troubleshooting

### Webcam not opening

- Close other apps using the camera (Teams, Zoom, Camera app).
- Try `VIDEO_SOURCE=1` for a second camera.
- Run PowerShell as your user (not over RDP without camera redirect).

### `Unable to open video source`

- Check file path exists.
- Use absolute paths on Windows.
- Prefer `.mp4` (H.264) for OpenCV compatibility.

### Low FPS

- Set `YOLO_MODEL=yolo11n.pt` (nano, fastest).
- Disable face recognition: `FACE_RECOGNITION_ENABLED=false`.
- Use a GPU build of PyTorch if available.

### Face always `Unknown`

- Use larger, frontal face photos in `known_faces`.
- Lower `FACE_MATCH_THRESHOLD` slightly (e.g. `0.35`).
- Ensure person bbox is large enough in frame.

### Port already in use

Change in `.env`:

```ini
PORT=8766
```

---

## 11. Project structure reference

```
Yolo26-Human-Detection/
├── app/
│   ├── main.py              # FastAPI web server
│   ├── pipeline.py          # Capture + inference loop
│   ├── detector.py          # YOLO + ByteTrack/BoT-SORT
│   ├── face_registry.py     # DeepFace identification
│   └── templates/           # Web UI
├── data/
│   ├── known_faces/         # Registered people
│   └── sample/              # Smoke test images
├── scripts/
│   └── smoke_test.py
├── requirements.txt
├── .env.example
└── run.py
```

---

## 12. Stopping the server

Press `Ctrl+C` in the terminal where `run.py` is running.

---

## 13. Next steps for grading / demo

1. Run smoke test and save `bus_detected.jpg` for the report.
2. Record a short screen capture of the web UI with webcam or sample video.
3. Document tracker comparison (ByteTrack vs BoT-SORT) if required by your course.
4. Include sample face registration screenshots in your submission.
