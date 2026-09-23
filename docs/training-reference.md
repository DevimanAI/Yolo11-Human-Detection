# Training & model reference (defense / deep dive)

Optional reading. Quick steps are in [README.md](README.md).

---

## App model spec

| Item | Value |
|------|-------|
| Model | YOLO11n (`yolo11n.pt`) |
| Class | `person` (COCO id 0) |
| Head | **Anchor-free** Detect on P3, P4, P5 |
| Params | ~2.6M |
| Tracking | ByteTrack / BoT-SORT (not trained with YOLO) |
| Face | DeepFace Facenet512 — pretrained gallery |

**YOLO11 vs YOLOv4:** Your old YOLOv4 folder uses anchors; **YOLO11 does not**. There is no anchor config in training YAML.

---

## Architecture (short)

```
Input 640×640 → Conv/C3k2 backbone → SPPF → C2PSA
              → PAN-FPN neck → Detect @ 3 scales → box + cls + DFL losses
```

| Block | Role |
|-------|------|
| Conv | Feature extraction, downsampling |
| C3k2 | Efficient CSP blocks |
| SPPF | Multi-scale context |
| C2PSA | Spatial attention |
| Detect | Anchor-free boxes at 3 resolutions |

Official spec: [yolo11.yaml](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/11/yolo11.yaml)

---

## Key training hyperparameters

File: `configs/train_yolo11n.yaml`. Full list: [Ultralytics cfg](https://docs.ultralytics.com/usage/cfg)

| Param | Default | Increase → | Decrease → |
|-------|---------|------------|------------|
| epochs | 50 | Better fit, overfit risk | Underfit |
| batch | 8 | Stable gradients, needs VRAM | Noisy |
| imgsz | 640 | Better small people, slower | Faster, miss small |
| lr0 | 0.01 | Faster, unstable | Safer fine-tune |
| mosaic | 1.0 | Robust crowded scenes | Less aug |
| box / cls / dfl | 7.5 / 0.5 / 1.5 | Emphasize that loss term | — |
| pretrained | true | Fine-tune from COCO | Train from scratch |

---

## Inference vs training

| Training | Runtime (`.env`) |
|----------|------------------|
| `epochs`, `lr0`, `mosaic` | Not used |
| — | `CONFIDENCE` / `conf` |
| — | `YOLO_MODEL` path |
| — | `TRACKER` yaml |
| — | `FACE_MATCH_THRESHOLD` |

---

## Dataset choice

| Dataset | Use here? |
|---------|-----------|
| CrowdHuman | Yes — person boxes |
| CASIA tampering | No — forgery detection |
| COCO person | Pretrain source of `yolo11n.pt` |

Default convert: **1532 train + 383 val** images (1915 total).

---

## Common defense questions

1. **Anchors?** YOLO11 is anchor-free; use `imgsz` and loss gains instead.  
2. **Train ByteTrack?** No — separate tracker config.  
3. **Train DeepFace CNN?** No — pretrained + your photos in `known_faces/`.  
4. **Why CrowdHuman not CASIA?** Task mismatch — no person bbox labels in CASIA.
