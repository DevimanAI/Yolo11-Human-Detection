# Train YOLO11 for person detection

## What you are training

Fine-tune **YOLO11n** (`yolo11n.pt`, pretrained on COCO) on pedestrian boxes from **CrowdHuman**.

**Not used:** [CASIA tampering dataset](https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset) — that is for forged-image detection, not people.

---

## GPU training (CUDA)

You have an **NVIDIA GPU** (e.g. RTX 4060). You do **not** need to install the full [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) separately.

| Requirement | Notes |
|-------------|--------|
| NVIDIA driver | Already installed if `nvidia-smi` works |
| CUDA PyTorch | Installed automatically by `setup-train.ps1` into `.venv` |

Training on GPU is **much faster** than CPU (often 10–50× for YOLO fine-tuning). After setup, you should see `CUDA available: True`.

---

## Everything stays inside this repo

Scripts set cache paths under the project folder so you can delete the whole repo after your defense:

| Path | Contents |
|------|----------|
| `.venv/` | Python packages (PyTorch, Ultralytics, …) |
| `.cache/` | pip cache, torch hub, ultralytics weights cache |
| `data/raw/`, `data/datasets/` | CrowdHuman download + YOLO dataset |
| `runs/` | Training outputs |
| `deepface_weights/` | DeepFace model weights |
| `.kaggle/` | Optional Kaggle API token (copy here instead of `%USERPROFILE%`) |
| `yolo11n.pt` | Downloaded base weights |

Remove all of the above:

```powershell
.\scripts\cleanup-all.ps1
```

---

## Quick steps (Windows)

```powershell
cd C:\Users\Megam\source\repos\Yolo11-Human-Detection

# 1. Environment (+ GPU PyTorch if NVIDIA detected)
.\scripts\setup-train.ps1

# 2. Download raw CrowdHuman (Kaggle — see below for credentials)
.\scripts\download_dataset.ps1

# 3. Convert to YOLO format — keeps 2000 train + 500 val only
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py

# 4. Train (~50 epochs by default; use -Epochs 5 for a quick test)
.\scripts\train_yolo11.ps1

# 5. Use trained weights
# Edit .env:  YOLO_MODEL=runs/detect/person_yolo11n/weights/best.pt
.\.venv\Scripts\python.exe scripts\smoke_test.py --model runs/detect/person_yolo11n/weights/best.pt
```

---

## Dataset size (2500 images)

| Split | Default count | Flag |
|-------|---------------|------|
| Train | 2000 | `--max-train 2000` (default) |
| Val | 500 | `--max-val 500` (default) |

The download script fetches **annotations + 2500 images only** (~1–2 GB), not the full **11 GB** Kaggle archive ([leducnhuan/crowdhuman](https://www.kaggle.com/datasets/leducnhuan/crowdhuman)).

Convert copies those into `data/datasets/person_crowdhuman/` for training.

Free disk after convert:

```powershell
Remove-Item -Recurse -Force data\raw\crowdhuman\Images, data\raw\crowdhuman\Images_val
```

Full 11 GB archive (optional): `.\scripts\download_dataset.ps1 -Full`

---

## Kaggle setup (one time)

1. Open https://www.kaggle.com/settings/api
2. **New token (`KGAT_...`):** copy it into `.kaggle\access_token` inside this repo (one line, no quotes)
   - Or set `KAGGLE_API_TOKEN=...` in `.env`
3. **Legacy key only:** use "Create Legacy API Key" and save as `.kaggle\kaggle.json` with `username` + `key`
4. Open [leducnhuan/crowdhuman](https://www.kaggle.com/datasets/leducnhuan/crowdhuman) and click **Download** once to accept the license

---

## Manual download (no Kaggle)

1. Get CrowdHuman from https://www.crowdhuman.org/
2. Put `Images/`, `annotation_train.odgt`, `annotation_val.odgt` under `data/raw/crowdhuman/`
3. Run `convert_crowdhuman.py` (same 2000/500 limits)

---

## Pipeline test without CrowdHuman

```powershell
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py --mini
.\scripts\train_yolo11.ps1 -Epochs 3 -Name smoke_train
```

This only checks that training runs — **do not** use smoke weights for the real demo.

---

## Config files

| File | Role |
|------|------|
| `configs/person_crowdhuman.yaml` | Dataset paths, 1 class: `person` |
| `configs/train_yolo11n.yaml` | Epochs, batch, lr, augmentations |

Override epochs/batch:

```powershell
.\scripts\train_yolo11.ps1 -Epochs 30 -Batch 4
```

---

## Export metrics (report / thesis figures)

```powershell
.\.venv\Scripts\python.exe scripts\export_metrics.py --run-dir runs/detect/person_yolo11n
```

Output: `docs/training_runs/`

---

## YOLO11 notes

- **Anchor-free** (no anchor boxes to configure — unlike YOLOv4/v5)
- Tracking (ByteTrack) is **separate** — not trained with the detector
- See [training-reference.md](training-reference.md) for hyperparameter details
