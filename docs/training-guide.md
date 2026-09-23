# YOLO11 Person Detection — Training Guide

This guide walks you through downloading a **person-detection** dataset, fine-tuning **YOLO11n**, and using the trained weights in the web demo.

> **Why not CASIA?** The [CASIA 2.0 Image Tampering dataset](https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset) detects **forged image regions**, not people. It has no YOLO bounding boxes for class `person` and does not match [`app/detector.py`](../app/detector.py). This project uses **CrowdHuman** (pedestrian boxes) instead.

---

## 1. Prerequisites

| Item | Notes |
|------|-------|
| Python 3.10+ on PATH | Use project `.venv` (see [run-and-test.md](run-and-test.md)) |
| Disk space | ~5–10 GB for CrowdHuman + training runs |
| GPU | Strongly recommended; CPU works for `--mini` smoke training only |
| Kaggle account | For automated CrowdHuman download (optional if you extract manually) |

---

## 2. One-time training setup

From repo root (PowerShell):

```powershell
.\scripts\setup-train.ps1
```

This reuses `.venv`, installs `requirements-train.txt`, and prints whether CUDA is available.

Linux/macOS:

```bash
bash scripts/setup-train.sh
```

---

## 3. Download CrowdHuman

### Option A — Kaggle (automated)

1. Create a Kaggle API token at https://www.kaggle.com/settings
2. Save `kaggle.json` to `%USERPROFILE%\.kaggle\kaggle.json` (Windows) or `~/.kaggle/kaggle.json`
3. Run:

```powershell
.\scripts\download_dataset.ps1
```

Default slug: `nkk754/crowdhuman-crowd-human-detection-dataset`. Override:

```powershell
.\scripts\download_dataset.ps1 -DatasetSlug "your-org/crowdhuman"
```

Files land in `data/raw/crowdhuman/` (gitignored).

### Option B — Official site (manual)

1. Download from https://www.crowdhuman.org/
2. Place `Images/`, `annotation_train.odgt`, and `annotation_val.odgt` under `data/raw/crowdhuman/`

### Option C — Smoke training only (no download)

```powershell
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py --mini
```

Builds 10 pseudo-labeled copies of `data/sample/bus.jpg` for pipeline verification — **not** for thesis final metrics. A 3-epoch smoke train on this tiny set will **not** generalize to new images; use full CrowdHuman for real `best.pt`.

---

## 4. Convert to YOLO format

Full conversion:

```powershell
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py
```

CPU-friendly subset (thesis experiments on laptop):

```powershell
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py --max-train 2000 --max-val 500
```

Output layout:

```
data/datasets/person_crowdhuman/
  images/train/
  images/val/
  labels/train/   # one .txt per image, class 0 = person
  labels/val/
```

Dataset config: [`configs/person_crowdhuman.yaml`](../configs/person_crowdhuman.yaml)

---

## 5. Fine-tune YOLO11n

Default hyperparameters: [`configs/train_yolo11n.yaml`](../configs/train_yolo11n.yaml)

```powershell
.\scripts\train_yolo11.ps1
```

Quick smoke run (3 epochs, small batch):

```powershell
.\scripts\train_yolo11.ps1 -Epochs 3 -Batch 4 -Name smoke_train
```

Underlying Python entry:

```powershell
.\.venv\Scripts\python.exe scripts\train_yolo11.py --epochs 50 --batch 8
```

Training writes to `runs/detect/person_yolo11n/` (gitignored).

---

## 6. Export metrics for thesis / defense

```powershell
.\.venv\Scripts\python.exe scripts\export_metrics.py --run-dir runs/detect/person_yolo11n
```

Copies `results.csv`, PR curves, confusion matrix, and `best.pt` into `docs/training_runs/` (committed for reports).

---

## 7. Use trained weights in the app

Edit `.env`:

```ini
YOLO_MODEL=runs/detect/person_yolo11n/weights/best.pt
```

Verify:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py --model runs/detect/person_yolo11n/weights/best.pt
.\.venv\Scripts\python.exe run.py
```

---

## 8. Recommended thesis experiment

| Step | Command | Purpose |
|------|---------|---------|
| Baseline eval | Evaluate `yolo11n.pt` on val split | Compare before fine-tune |
| Fine-tune | `train_yolo11.ps1` with 50 epochs | Main result |
| Ablation | `--imgsz 416` or lower `mosaic` | Show parameter understanding |

Document **mAP50**, **mAP50-95**, precision, recall from `results.csv`.

---

## 9. Troubleshooting

| Issue | Fix |
|-------|-----|
| Kaggle 403 | Check `kaggle.json` permissions; accept dataset license on Kaggle website |
| No ODGT found | Confirm files under `data/raw/crowdhuman/` |
| CUDA OOM | Lower `--batch` (4 or 2) or `--imgsz 416` |
| Training very slow on CPU | Use `--max-train 200` and `-Epochs 5` |
| `ModuleNotFoundError: ultralytics` | Run inside `.venv` — never Store Python |

---

## 10. Related docs

- [training-params-defense-fa.md](training-params-defense-fa.md) — Persian Q&A for defense (hyperparameters, anchors, CNN)
- [deepface-gallery-fa.md](deepface-gallery-fa.md) — Face gallery setup (not CNN training)
- [thesis/](thesis/) — Full Persian thesis draft (~40 pages)
