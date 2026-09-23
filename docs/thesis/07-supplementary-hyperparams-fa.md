# پیوست تکمیلی — شرح مفصل پارامترهای آموزش (برای دفاع)

این فصل تکمیلی برای پاسخ به سؤالات داور درباره «اگر پارامeter X را تغییر دهید چه می‌شود» به پایان‌نامه افزوده شده است. محتوا هم‌پوشان با `docs/training-reference.md` است.

---

## 7-1. پارامeterهای مربوط به داده

### imgsz (اندازه تصویر آموزش)

پیش‌فرض **640**. تصویر به مربع 640×640 resize می‌شود (با letterbox).  
- **افزایش (832, 1024):** person کوچک در جمعیت بهتر دیده می‌شود؛ حافظه و زمان ↑  
- **کاهش (416):** FPS inference ↑؛ risk از دست دادن افراد دور  

### batch (اندازه دسته)

تعداد تصویر در هر gradient step.  
- **GPU 6GB:** batch=4–8  
- **GPU 12GB+:** batch=16–32  
- **CPU smoke:** batch=2–4  

### workers

threadهای dataloader. روی Windows گاهی `workers=0` پایدارتر است.

---

## 7-2. پارامeterهای بهینه‌ساز

### lr0 (نرخ یادگیری اولیه)

0.01 برای SGD-family. Fine-tune از COCO معمولاً 0.001–0.01.  
**خیلی بالا:** loss نوسان؛ **خیلی پایین:** همگرایی کند.

### lrf

ضریب LR نهایی = lr0 × lrf. schedule cosine/linear در epochها.

### momentum و weight_decay

momentum=0.937 هموارسازی gradient.  
weight_decay=5e-4 L2 regularization — against overfit روی dataset کوچک.

### optimizer=auto

Ultralytics: AdamW برای epoch<100 و batch کوچک؛ MuSGD برای run طولانی.

---

## 7-3. Augmentation

### mosaic

چهار تصویر در یک tile. برای CrowdHuman بسیار مفید — شبیه‌سازی شلوغی.  
`close_mosaic=10`: 10 epoch آخر بدون mosaic برای fine localization.

### mixup / copy_paste

در person detection گاهی copy_paste فعال می‌شود؛ preset پیش‌فرض پروژه mixup=0.

### HSV jitter (hsv_h, hsv_s, hsv_v)

تغییر رنگ/نور برای generalization outdoor/indoor.

### fliplr=0.5

flip افقی — برای person symmetric مناسب.

---

## 7-4. Loss gains

| Gain | نقش |
|------|-----|
| box=7.5 | وزن خطای موقعیت جعبه |
| cls=0.5 | وزن classification (تک کلاسه person) |
| dfl=1.5 | Distribution Focal Loss — anchor-free borders |

**سؤال:** «anchor عوض کنیم؟» — **YOLO11 anchor ندارد**؛ dfl و TaskAlignedAssigner جایگزین شده‌اند.

---

## 7-5. نتایج smoke train (مرجع عددی)

Run: `smoke_train` — mini dataset (8 train, 2 val), 3 epochs, CPU:

| metrics/mAP50 | 0.278 |
| metrics/mAP50-95 | 0.265 |
| metrics/recall | 1.0 |

Precision پایین به‌دلیل dataset بسیار کوچک و تکراری bus.jpg است — **جایگزین گزارش CrowdHuman کامل نیست**.

---

## 7-6. پارامeterهای inference در اپ

| .env | Training equivalent |
|------|---------------------|
| CONFIDENCE=0.5 | conf at predict — نه learned |
| YOLO_MODEL | path to best.pt |
| TRACKER | separate yaml — MOT |

---

## 7-7. چک‌لیست سوالات داور

1. **YOLO11 anchor دارد؟** خیر — anchor-free از v8  
2. **CASIA چرا نیامد؟** tampering detection ≠ person bbox  
3. **DeepFace train شد؟** pretrained + gallery  
4. **ByteTrack train شد؟** خیر — post-processing tracker  
5. **چند پارامتر YOLO11n؟** ~2.58M fused  
6. **Loss functions?** box + cls + dfl  
7. **چطور overfit را ببینیم؟** train loss ↓ و val mAP plateau یا ↓  

---

## 7-8. مراجع سریع

- configs/train_yolo11n.yaml  
- docs/train-yolo.md  
- Ultralytics cfg: https://docs.ultralytics.com/usage/cfg  
