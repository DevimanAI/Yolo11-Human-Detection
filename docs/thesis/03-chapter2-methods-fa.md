# فصل ۲ — روش تحقیق، ابزار و مجموعه‌داده

## 2-1. روش کلی تحقیق

رویکرد **عملی–توسعه‌ای** (Design Science):  
1. پیاده‌سازی سامانه inference  
2. انتخاب dataset هم‌راستا با مسئله  
3. Fine-tune YOLO11n  
4. ارزیابی کیفی و کمی  
5. مستندسازی hyperparameterها  

## 2-2. سخت‌افزار و نرم‌افزار

| جزء | مشخصات پیشنهادی |
|-----|-----------------|
| OS | Windows 10/11 |
| Python | 3.10+ در `.venv` |
| PyTorch | همراه ultralytics (CPU/GPU) |
| GPU | NVIDIA با CUDA (توصیه برای آموزش) |
| RAM | 8 GB+ |
| وب‌کم | اختیاری برای demo |

پکیج‌ها: `requirements.txt` (runtime)، `requirements-train.txt` (kaggle, tensorboard)، `requirements-face.txt` (DeepFace).

## 2-3. مجموعه‌داده CrowdHuman

### 2-3-1. دلیل انتخاب

- برچسب **pedestrian bounding box**  
- صحنه‌های شلوغ (هم‌راستا با کاربرد نظارت)  
- فرمت ODGT قابل تبدیل به YOLO  

### 2-3-2. فرمت YOLO پس از تبدیل

هر خط label: `class x_center y_center width height` (normalized 0–1).  
تک کلاس: `0 person`.

اسکریپت: `scripts/convert_crowdhuman.py`  
از `vbox` یا `fbox` در ODGT استفاده می‌کند.

### 2-3-3. تقسیم train/val

طبق annotation_train / annotation_val رسمی CrowdHuman.  
برای آزمایش روی CPU: `--max-train 2000`.

## 2-4. Hyperparameterهای آموزش

فایل: `configs/train_yolo11n.yaml`

| پارامتر | مقدار پیش‌فرض | توجیه |
|---------|---------------|--------|
| model | yolo11n.pt | transfer learning از COCO |
| epochs | 50 | تعادل fit/time |
| imgsz | 640 | استاندارد YOLO |
| batch | 8 | بسته به VRAM |
| lr0 | 0.01 | fine-tune استاندارد SGD/AdamW |
| mosaic | 1.0 | robustness جمعیت |
| amp | true | سرعت GPU |

جزئیات کامل: `docs/training-reference.md`.

## 2-5. معیارهای ارزیابی

- **mAP50**, **mAP50-95** روی val  
- **Precision / Recall**  
- **FPS** inference روی CPU/GPU  
- **MOTA** (اختیاری) برای tracker — خارج از آموزش detector  

## 2-6. معماری نرم‌افزار (سطح سیستم)

```
Webcam/Video → OpenCV Capture → YOLO11 track → (DeepFace) → Annotated Frame → MJPEG → Browser
```

ماژول‌ها: `detector.py`, `pipeline.py`, `face_registry.py`, `main.py`.

## 2-7. اخلاق و حریم خصوصی

- دمو روی webcam شخصی یا ویدئو anonymized  
- known_faces فقط با رضایت افراد  
- عدم ذخیره ویدئو بدون مجوز  

## 2-8. جمع‌بندی فصل

ابزار، dataset و protocol آموزش تعریف شد. فصل ۳ پیاده‌سازی و نتایج عددی را گزارش می‌کند.
