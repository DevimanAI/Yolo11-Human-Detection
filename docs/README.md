# Documentation index

Start here for setup, training, and the live demo.

---

## Fast path (copy-paste)

### A. Run the demo (no training)

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\python.exe scripts\smoke_test.py
.\.venv\Scripts\python.exe run.py
```

Open http://127.0.0.1:8765

### B. Train YOLO11 (person detection)

```powershell
.\scripts\setup-train.ps1
.\scripts\download_dataset.ps1
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py
.\scripts\train_yolo11.ps1
```

Uses **1532 train + 383 val** (1915 total) from [leducnhuan/crowdhuman](https://www.kaggle.com/datasets/leducnhuan/crowdhuman). Details: [train-yolo.md](train-yolo.md)

### C. Recognize your face (DeepFace)

DeepFace uses a **pretrained** model — you add photos of yourself, not train a CNN from scratch.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-face.txt
.\scripts\register_face.ps1 -Name "YourName"
# copy 2-3 front-facing photos into the folder it creates
.\.venv\Scripts\python.exe scripts\build_face_gallery.py --build
.\.venv\Scripts\python.exe run.py
```

Details: [face-recognition.md](face-recognition.md)

---

## All guides

| Doc | When to read |
|-----|----------------|
| [run-demo.md](run-demo.md) | Install, webcam demo, troubleshooting |
| [train-yolo.md](train-yolo.md) | Dataset, fine-tune, use `best.pt` in the app |
| [face-recognition.md](face-recognition.md) | Register your face, tune matching threshold |
| [training-reference.md](training-reference.md) | Hyperparameters, YOLO11 architecture, defense Q&A |

---

## Scripts (what each does)

| Script | Purpose |
|--------|---------|
| `setup.ps1` | Create `.venv`, install runtime deps |
| `setup-train.ps1` | Add training deps (kaggle, tensorboard) |
| `download_dataset.ps1` | Download CrowdHuman from Kaggle |
| `convert_crowdhuman.py` | Build YOLO dataset (default 1532/383) |
| `train_yolo11.ps1` | Fine-tune YOLO11n |
| `register_face.ps1` | Create folder for your face photos |
| `build_face_gallery.py` | Verify DeepFace gallery |
| `smoke_test.py` | Test detection on sample bus image |
| `run.py` | Start web demo |
| `cleanup-all.ps1` | Delete `.venv`, datasets, caches (after defense) |

All downloads and caches stay under this repo (`.venv`, `.cache`, `data/`, `runs/`). See [train-yolo.md](train-yolo.md#everything-stays-inside-this-repo).
