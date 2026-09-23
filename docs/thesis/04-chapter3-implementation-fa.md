# فصل ۳ — پیاده‌سازی، آموزش و نتایج

## 3-1. ساختار مخزن پروژه

```
app/           # FastAPI + YOLO pipeline
configs/       # dataset YAML + train hyperparameters
scripts/       # setup, download, convert, train, export
data/
  datasets/    # YOLO person (generated)
  known_faces/ # DeepFace gallery
  sample/      # smoke test
docs/
  thesis/      # این پایان‌نامه
  training_runs/ # نمودارها و CSV export
```

## 3-2. لایه تشخیص و ردیابی

کلاس `HumanDetectorTracker` در `detector.py`:

```python
results = self.model.track(
    source=frame_bgr,
    persist=True,
    tracker=self.tracker,
    classes=[0],  # person
    conf=self.confidence,
)
```

- `PERSON_CLASS_ID = 0` مطابق COCO  
- خروجی: bbox، confidence، track_id  

## 3-3. لایه چهره (اختیاری)

`FaceRegistry` در startup embedding می‌سازد؛ `identify()` فاصله کسینوسی را با آستانه `FACE_MATCH_THRESHOLD` مقایسه می‌کند.

اسکریپت اعتبارسنجی: `scripts/build_face_gallery.py --build`

## 3-4. رابط وب

FastAPI + MJPEG در `/video`.  
Endpoint `/api/status` آمار FPS و تعداد افراد را برمی‌گرداند.

## 3-5. فرآیند آموزش (reproducible)

### گام ۱ — محیط
```powershell
.\scripts\setup-train.ps1
```

### گام ۲ — دانلود
```powershell
.\scripts\download_dataset.ps1
```

### گام ۳ — تبدیل
```powershell
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py
```

### گام ۴ — آموزش
```powershell
.\scripts\train_yolo11.ps1
```

### گام ۵ — export
```powershell
.\.venv\Scripts\python.exe scripts\export_metrics.py --run-dir runs/detect/person_yolo11n
```

## 3-6. نتایج آموزش

### 3-6-1. Baseline (pretrained yolo11n.pt)

- Smoke test روی `bus.jpg`: **4 person** detect شده  
- Inference CPU: ~43 ms/image (Ultralytics benchmark)  
- بدون fine-tune اختصاصی روی CrowdHuman  

### 3-6-2. Smoke fine-tune (mini dataset — 10 تصویر bus)

برای **تأیید pipeline آموزش** (نه گزارش نهایی نمره)، 3 epoch روی mini dataset (`convert_crowdhuman.py --mini`) اجرا شد:

| معیار | مقدار |
|--------|--------|
| epochs | 3 |
| train images | 8 |
| val images | 2 |
| mAP50 | 0.278 |
| mAP50-95 | 0.265 |
| Recall | 1.0 |
| Precision | 0.013 |
| weights | `runs/detect/smoke_train/weights/best.pt` |

Export: `docs/training_runs/smoke_train/` (results.csv, results.png, best.pt)

> **گزارش نهایی پایان‌نامه:** پس از `download_dataset.ps1` و تبدیل کامل CrowdHuman، `train_yolo11.ps1` با 50 epoch اجرا کنید و metrics را با `export_metrics.py` جایگزین کنید.

### 3-6-3. Fine-tune کامل CrowdHuman (پیشنهادی)

| معیار | مقدار (پس از train کامل) |
|--------|---------------------------|
| mAP50 | [پس از 50 epoch — results.csv] |
| mAP50-95 | [پس از 50 epoch] |
| epochs | 50 (پیش‌فرض configs/train_yolo11n.yaml) |
| weights | runs/detect/person_yolo11n/weights/best.pt |

شکل 3-1: منحنی `results.png` — box_loss, cls_loss, mAP  
شکل 3-2: `confusion_matrix.png`  
شکل 3-3: `bus_detected.jpg` — خروجی inference  

## 3-7. ادغام وزن آموزش‌دیده در اپ

`.env`:
```
YOLO_MODEL=runs/detect/person_yolo11n/weights/best.pt
```

## 3-8. تست عملکرد runtime

| سناریو | نتیجه |
|--------|--------|
| smoke_test.py | PASS |
| run.py `/api/status` | 200 OK |
| صفحه اصلی `/` | 200 OK |
| Face ID بدون requirements-face | gracefully disabled |

## 3-9. Ablation پیشنهادی (گزارش در دفاع)

1. `imgsz=416` vs `640` — trade-off speed/small person  
2. `mosaic=0` vs default — effect on crowded scene  
3. ByteTrack vs BoT-SORT — track stability  

## 3-10. جمع‌بندی فصل

سامانه end-to-end پیاده‌سازی شد؛ pipeline آموزش مستند و قابل تکرار است. فصل ۴ نتایج را تحلیل و محدودیت‌ها را بیان می‌کند.
