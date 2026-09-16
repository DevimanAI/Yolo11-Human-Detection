# Run and Test Guide — YOLO Human Detection & Tracking

This guide explains how to set up, run, and verify the project on **Windows** at:

`C:\Users\Megam\source\repos\Yolo11-Human-Detection`

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

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/) and check **“Add python.exe to PATH”**. The `py` launcher is optional and often missing.
2. Open **PowerShell** (not CMD) for the commands below.
3. Allow the app through Windows Firewall when prompted (port **8765**).
4. Always install packages into **`.venv`**. Microsoft Store Python user-site paths are too long for PyTorch (**WinError 206**), which is why `ultralytics` goes missing.

---

## 2. Clone the repository

```powershell
mkdir C:\Users\Megam\source\repos -Force
cd C:\Users\Megam\source\repos
git clone https://github.com/DevimanAI/Yolo11-Human-Detection.git
cd Yolo11-Human-Detection
```

If the folder already exists:

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
git pull origin main
```

---

## 3. Publish to GitHub

Use this path if **Origin HTTPS clone fails** (2FA / credential issues) or you want the project on **your GitHub account** instead of Origin.

**Do not use Git username/password over HTTPS** — GitHub requires a personal access token or the **GitHub CLI browser login**, which works with 2FA.

### Step A — Install and authenticate GitHub CLI

1. Install [GitHub CLI](https://cli.github.com/) for Windows.
2. In PowerShell:

```powershell
gh auth login
```

Choose:

- **GitHub.com**
- **HTTPS**
- **Login with a web browser** (recommended; works with 2FA)

### Step B — Get the project onto your PC

**Option 1 — You already have the folder** (copied from cloud agent, USB, zip, etc.) with a `.git` directory:

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
.\scripts\setup-github.ps1
```

**Option 2 — You only have the git bundle** (no `.git` yet). The bundle ships at `scripts\yolo11-human-detection.bundle` (< 1 MB, all branches):

```powershell
mkdir C:\Users\Megam\source\repos -Force
cd C:\Users\Megam\source\repos
# Copy the project folder here first, or download scripts\yolo11-human-detection.bundle into scripts\
.\Yolo11-Human-Detection\scripts\setup-github.ps1 -TargetDir C:\Users\Megam\source\repos\Yolo11-Human-Detection
```

Or restore manually, then publish:

```powershell
git clone C:\path\to\scripts\yolo11-human-detection.bundle C:\Users\Megam\source\repos\Yolo11-Human-Detection
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection
.\scripts\setup-github.ps1
```

**Option 3 — Linux / macOS:**

```bash
./scripts/setup-github.sh --target-dir ~/source/repos/Yolo11-Human-Detection
```

### What the script does

1. Verifies `gh` is installed and you ran `gh auth login`.
2. Creates a **private** repo `Yolo11-Human-Detection` on your GitHub account.
3. Adds remote `github` and pushes all branches.

If remote `github` already exists, it only pushes updates.

### After publishing

Clone from GitHub on any machine (no Origin 2FA issues):

```powershell
git clone https://github.com/YOUR_USERNAME/Yolo11-Human-Detection.git C:\Users\Megam\source\repos\Yolo11-Human-Detection
```

Replace `YOUR_USERNAME` with your GitHub username.

### Regenerate the bundle (maintainers)

From repo root, if history changes and the bundle is not committed:

```powershell
git bundle create scripts/yolo11-human-detection.bundle --all
```

Include in git only if the file stays under 1 MB; otherwise document this command for users.

---

## 4. Create virtual environment and install (recommended)

From the repo root:

```powershell
.\scripts\setup.ps1
```

This runs `python -m venv .venv`, upgrades pip **inside the venv**, installs `requirements.txt`, and copies `.env.example` to `.env` if needed.

You do **not** need to activate the venv. Call the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe run.py
```

### Manual equivalent

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

If you want to activate anyway and `Activate.ps1` is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

**Do not** run `pip install -r requirements.txt` with Microsoft Store `python` outside `.venv`. That writes to a long `LocalCache\local-packages` path and PyTorch install fails with **WinError 206**.

---

## 5. Optional face-recognition extras

Core demo (detection + tracking + web UI) does **not** need TensorFlow.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-face.txt
```

**First run notes:**

- Ultralytics downloads `yolo11n.pt` automatically (~5 MB).
- DeepFace downloads face model weights on first face recognition use (~100 MB).
- Core install may take several minutes (PyTorch). Face extras add TensorFlow and take longer.

---

## 6. Configure environment

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

## 7. Smoke test (no webcam required)

Verifies YOLO download, person detection, and sample output:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

**Expected output:**

- Downloads `data\sample\bus.jpg` if missing.
- Prints `Detected N person(s)` with bounding boxes.
- Saves `data\sample\bus_detected.jpg`.

Open the annotated image to confirm green boxes around people.

**Success criteria:** at least one person detected on the bus sample (typically 3–4).

---

## 8. Register known faces (optional)

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

## 9. Start the web demo

```powershell
.\.venv\Scripts\python.exe run.py
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

## 10. Test matrix

| Test | Steps | Pass criteria |
|------|--------|---------------|
| Dependency install | `.\scripts\setup.ps1` | No errors; `.venv` exists |
| Model download | `.\.venv\Scripts\python.exe scripts\smoke_test.py` | `yolo11n.pt` present, persons detected |
| Web server | `.\.venv\Scripts\python.exe run.py` | Page loads at port 8765 |
| Webcam | Default `VIDEO_SOURCE=0` | Stream shows live video with boxes |
| Video file | Set path in UI or `.env` | File plays with tracking IDs stable across frames |
| Face ID | Install `requirements-face.txt`, add photos under `known_faces` | Known person labeled by name |
| Tracker swap | `TRACKER=botsort.yaml` in `.env` | Tracking still works after restart |

---

## 11. Troubleshooting

### `py` is not recognized

Use `python -m venv .venv` or `.\scripts\setup.ps1`. The Windows `py` launcher is not required.

### `Activate.ps1` is not recognized

The venv was never created (often because `py` failed first). Run `.\scripts\setup.ps1`, then use `.\.venv\Scripts\python.exe` instead of activating.

### `ModuleNotFoundError: No module named 'ultralytics'`

Dependencies were installed into Microsoft Store Python, not `.venv`. Re-run setup and launch with `.\.venv\Scripts\python.exe`.

### `WinError 206` The filename or extension is too long

PyTorch cannot install into Store Python’s user-site path. Use the project `.venv` (much shorter). If a venv install still fails, enable Windows long paths (admin PowerShell):

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Then reboot and retry `.\scripts\setup.ps1`.

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

## 12. Project structure reference

```
Yolo11-Human-Detection/
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
│   ├── setup.ps1
│   ├── setup.sh
│   ├── smoke_test.py
│   ├── setup-github.ps1
│   ├── setup-github.sh
│   └── yolo11-human-detection.bundle
├── requirements.txt
├── requirements-face.txt
├── .env.example
└── run.py
```

---

## 13. Stopping the server

Press `Ctrl+C` in the terminal where `run.py` is running.

---

## 14. Next steps for grading / demo

1. Run smoke test and save `bus_detected.jpg` for the report.
2. Record a short screen capture of the web UI with webcam or sample video.
3. Document tracker comparison (ByteTrack vs BoT-SORT) if required by your course.
4. Include sample face registration screenshots in your submission.
