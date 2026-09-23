# راهنمای فنی آموزش و دفاع پروژه — YOLO11 Human Detection

این سند برای **پرسش‌های احتمالی هیئت داور** درباره معماری مدل، پارامترهای آموزش، تفاوت inference و training، و انتخاب مجموعه‌داده تهیه شده است.

---

## ۱. مشخصات مدل در اپلیکیشن (هم‌خوان با کد)

| مورد | مقدار در پروژه | منبع در کد |
|------|----------------|------------|
| خانواده مدل | Ultralytics **YOLO11n** | `YOLO_MODEL=yolo11n.pt` |
| کلاس | **person** (تک‌کلاسه در fine-tune؛ id=0 در COCO) | `PERSON_CLASS_ID = 0` در `detector.py` |
| ورودی inference | همان اندازه‌ای که Ultralytics روی فریم اعمال می‌کند (معمولاً 640) | `model.track(source=frame)` |
| ردیاب | ByteTrack یا BoT-SORT | `TRACKER=bytetrack.yaml` |
| آستانه تشخیص | `CONFIDENCE` (پیش‌فرض 0.5) | `.env` → `conf=` در track |
| چهره | Facenet512 اختیاری | `face_registry.py` |

**YOLO26:** نام قدیمی در مسیرهای clone اشتباه بود؛ مدل واقعی **`yolo11n.pt`** است.

**Anchors:** YOLO11 **anchor-free** است (مثل YOLOv8+). Anchor در YOLOv3–v5 بود؛ در YOLO11 **تنظیم anchor وجود ندارد**.

---

## ۲. معماری YOLO11n — لایه‌های CNN

### ۲-۱. جریان کلی

```
Input (640×640×3)
  → Backbone (Conv + C3k2 + SPPF + C2PSA)
  → Neck (PAN-FPN: Upsample + Concat + C3k2)
  → Head (Detect روی P3/8, P4/16, P5/32)
  → خروجی: bbox + confidence + class
```

منبع: [yolo11.yaml رسمی Ultralytics](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/11/yolo11.yaml)

### ۲-۲. اجزای اصلی

| بلوک | نقش | اثر روی تشخیص انسان |
|------|-----|---------------------|
| **Conv** | استخراج ویژگی با فیلتر 3×3، stride برای downsample | لبه‌ها، بافت، اشکال |
| **C3k2** | CSP bottleneck با kernel کوچک‌تر؛ جایگزین C2f | کارایی بهتر نسبت به v8 |
| **SPPF** | Spatial Pyramid Pooling Fast | زمینه چند مقیاس در یک map |
| **C2PSA** | توجه مکانی (Spatial Attention) | تمرکز روی نواحی مهم (سر/بدن در جمعیت) |
| **Detect** | سر anchor-free سه مقیاس | اشخاص کوچک (P3)، متوسط (P4)، بزرگ (P5) |

### ۲-۳. مقیاس YOLO11n

| معیار | مقدار تقریبی |
|--------|--------------|
| پارامتر | ~2.6M |
| GFLOPs | ~6.6 |
| لایه | 181 |
| depth_multiple | 0.50 |
| width_multiple | 0.25 |
| max_channels | 1024 |

**سؤال داور:** «فیلتر Conv چه می‌کند؟»  
**پاسخ:** کانولوشن kernel روی پنجره محلی تصویر slide می‌کند؛ با ترکیب channelها feature map می‌سازد. stride=2 اندازه فضایی را نصف و receptive field را بزرگ‌تر می‌کند.

---

## ۳. Anchor چیست و چرا در YOLO11 نیست؟

### YOLO قدیم (v5 و قبل‌تر)

- برای هر سلول grid چند **anchor box** از پیش تعریف‌شده (مثلاً 80×80، 40×40) داشت.
- شبکه **offset** نسبت به anchor را پیش‌بینی می‌کرد.
- تغییر anchor در yaml → تغییر prior اندازه جعبه.

### YOLO11 (anchor-free)

- هر نقطه روی feature map مستقیماً **فاصله تا چهار لبه** (LTRB) را با **DFL** (Distribution Focal Loss) مدل می‌کند.
- تخصیص نمونه مثبت: **TaskAlignedAssigner** (top-k=10, α=0.5, β=6.0).
- **اگر بپرسند «anchor را چطور عوض کنیم؟»:** در YOLO11 این مفهوم حذف شده؛ به جای آن `imgsz`، augmentation و `box`/`dfl` loss gains را تنظیم کنید.

---

## ۴. تابع زیان (Loss) در آموزش

| جزء | gain پیش‌فرض | معنی |
|-----|--------------|------|
| box_loss | 7.5 | دقت مختصات جعبه |
| cls_loss | 0.5 | احتمال کلاس person |
| dfl_loss | 1.5 | توزیع مرز جعبه (anchor-free) |

**افزایش `box`:** مدل بیشتر روی localization تمرکز می‌کند — مفید اگر bbox لغزان است.  
**افزایش `cls`:** وقتی false positive کلاس زیاد است (در تک‌کلاسه کمتر ملموس است).

---

## ۵. جدول پارامترهای آموزش (Ultralytics)

منبع: [docs.ultralytics.com/usage/cfg](https://docs.ultralytics.com/usage/cfg)

| پارامتر | پیش‌فرض | اگر زیاد شود | اگر کم شود |
|---------|---------|--------------|------------|
| **epochs** | 50–100 | overfit احتمالی | underfit |
| **batch** | 8–16 | پایداری gradient؛ نیاز VRAM | نویز؛ آموزش کندتر |
| **imgsz** | 640 | اشخاص کوچک بهتر؛ کندتر | سریع‌تر؛ از دست دادن کوچک‌ها |
| **lr0** | 0.01 | یادگیری تند؛ ناپایدار | fine-tune امن‌تر |
| **lrf** | 0.01 | کف learning rate نهایی | — |
| **momentum** | 0.937 | SGD هموارتر | — |
| **weight_decay** | 0.0005 | regularization بیشتر | overfit |
| **warmup_epochs** | 3 | شروع پایدار | — |
| **mosaic** | 1.0 | robustness صحنه شلوغ | آموزش سریع‌تر ولی شکننده |
| **mixup** | 0.0 | blending تصاویر | — |
| **close_mosaic** | 10 | epoch پایانی بدون mosaic | — |
| **patience** | 20 | صبر early stopping | توقف زودهنگام |
| **optimizer** | auto | AdamW (<100 epoch) یا MuSGD | — |
| **amp** | true | سرعت + حافظه GPU | FP32 پایدارتر |
| **pretrained** | true | fine-tune از COCO (توصیه) | از صفر — داده و GPU زیاد |
| **freeze** | none | فقط head آموزش | — |
| **workers** | 4 | بارگذاری سریع‌تر dataloader | — |
| **cache** | false | cache=disk برای IO کند | — |

فایل پروژه: [`configs/train_yolo11n.yaml`](../configs/train_yolo11n.yaml)

---

## ۶. پارامترهای inference (اپ) — جدا از آموزش

| پارامتر | زمان | اثر |
|---------|------|-----|
| `CONFIDENCE` / `conf` | inference | بالاتر → جعبه کمتر، دقت بیشتر، recall کمتر |
| `classes=[0]` | inference | فقط person از 80 کلاس COCO |
| `persist=True` | track | حفظ track id بین فریم‌ها |
| ByteTrack `track_high_thresh` | yaml ردیاب | جعبه‌های ضعیف‌تر هم associate می‌شوند |
| `FACE_MATCH_THRESHOLD` | DeepFace | تشخیص نام vs Unknown |

**نکته دفاع:** آموزش `conf` را یاد نمی‌گیرد؛ روی validation با PR curve آستانه عملیاتی انتخاب می‌شود.

---

## ۷. مجموعه‌داده — چرا CASIA نیست؟

| مجموعه | کاربرد | مناسب این پروژه؟ |
|--------|---------|------------------|
| [CASIA Tampering](https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset) | تشخیص دستکاری/جعل تصویر | **خیر** — bbox person ندارد |
| **CrowdHuman** | pedestrian در جمعیت | **بله** — fine-tune YOLO |
| COCO person | همان دامنه pretrain | baseline / مقایسه |
| `known_faces/` | gallery چهره | DeepFace — نه YOLO |

---

## ۸. ردیابی (ByteTrack / BoT-SORT) — آموزش نمی‌شود

ردیاب جدا از وزن YOLO است:

- **ByteTrack:** association با detection با conf بالا و پایین
- **BoT-SORT:** + motion + Re-ID اختیاری

تغییر `TRACKER=botsort.yaml` در `.env` بدون retrain YOLO ممکن است.

---

## ۹. سناریوهای «اگر X را تغییر دهم؟»

| هدف | پارامتر پیشنهادی |
|-----|------------------|
| FPS بالاتر در demo | `yolo11n.pt`، `imgsz=416`، DeepFace خاموش |
| recall بیشتر در جمعیت | `conf` پایین‌تر (0.35)، fine-tune روی CrowdHuman |
| جعبه پایدارتر | `box` gain بالاتر در آموزش؛ ByteTrack |
| overfit روی داده کم | `weight_decay`↑، `mosaic`↑، epoch کمتر |
| آموزش روی CPU | `--max-train 200`، `epochs=5`، `batch=2` |

---

## ۱۰. معیارهای ارزیابی

| معیار | معنی |
|--------|------|
| mAP50 | میانگین AP با IoU≥0.5 |
| mAP50-95 | AP روی IoU 0.5 تا 0.95 — سخت‌گیرانه‌تر |
| Precision | TP / (TP+FP) |
| Recall | TP / (TP+FN) |
| box_loss, cls_loss, dfl_loss | منحنی‌های `results.csv` |

خروجی آموزش: `runs/detect/person_yolo11n/` → export با `scripts/export_metrics.py`

---

## ۱۱. یک‌صفحه‌ای مشخصات برای اسلاید دفاع

```
Model:     YOLO11n (Ultralytics 8.x)
Task:      Object Detection — class: person
Input:     640×640 (training default)
Head:      Anchor-free Detect (P3, P4, P5)
Loss:      box + cls + DFL (TaskAlignedAssigner)
Pretrain:  COCO (yolo11n.pt)
Fine-tune: CrowdHuman → configs/person_crowdhuman.yaml
Tracking:  ByteTrack (MOT, not trained with detector)
Face ID:   DeepFace Facenet512 (pretrained gallery)
Runtime:   FastAPI + OpenCV MJPEG
Smoke run: mAP50=0.278, mAP50-95=0.265 (3 ep, mini dataset — see docs/training_runs/smoke_train/)
```

---

## ۱۲. منابع

- Ultralytics YOLO11 YAML: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/11/yolo11.yaml
- Ultralytics Config: https://docs.ultralytics.com/usage/cfg
- YOLOv11 Architecture Overview: https://arxiv.org/html/2410.17725
- CrowdHuman: https://www.crowdhuman.org/
- ByteTrack paper (ردیابی)
- DeepFace library documentation
