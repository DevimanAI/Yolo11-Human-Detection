# فصل ۱ — مرور پیشینه و ادبیات

## 1-1. تشخیص شیء و YOLO

### 1-1-1. Detectorهای دو مرحله‌ای و تک‌مرحله‌ای

R-CNN و مشتقات ابتدا region proposal تولید می‌کنند سپس classify می‌کنند. YOLO کل تصویر را یک‌بار از CNN عبور می‌دهد و مستقیماً bbox و class پیش‌بینی می‌کند—مناسب ویدئو realtime.

### 1-1-2. تکامل YOLO تا نسخه ۱۱

| نسخه | نکته کلیدی |
|------|------------|
| YOLOv3–v5 | استفاده از **anchor boxes** |
| YOLOv8+ | **Anchor-free**، DFL، TaskAlignedAssigner |
| YOLO11 | C3k2، C2PSA، بهبود efficiency |

**پاسخ دفاع:** YOLO11 anchor ندارد؛ YOLOv5 anchor داشت. پروژه ما YOLO11 است.

### 1-1-3. معماری YOLO11n

Backbone: Conv layers با stride 2 برای pyramid P1…P5.  
Neck: PAN-FPN با upsample و concat.  
Head: Detect module روی P3 (اشیاء کوچک)، P4 (متوسط)، P5 (بزرگ).

Parámetros YOLO11n: حدود 2.6M پارامتر، 6.6 GFLOPs (منبع: Ultralytics model yaml).

## 1-2. ردیابی چند شیء (MOT)

Detection موقعیت لحظه‌ای می‌دهد؛ MOT هویت زمانی (track id) می‌دهد.

### 1-2-1. ByteTrack

با استفاده از detectionهای high و low confidence، association قوی در occlusion. فایل `bytetrack.yaml` در Ultralytics.

### 1-2-2. BoT-SORT

ترکیب Kalman filter و appearance embedding؛ در برخی صحنه‌ها پایدارتر.

## 1-3. شناسایی چهره

DeepFace framework چند مدل (Facenet512، VGG-Face، ArcFace) را برای embedding یکپارچه می‌کند. در این پروژه **transfer learning**: وزن ثابت، gallery محلی.

## 1-4. مجموعه‌داده‌های مرتبط

| Dataset | کاربرد |
|---------|--------|
| COCO | 80 کلاس شامل person — pretrain yolo11n |
| CrowdHuman | pedestrian crowded scenes — fine-tune |
| WiderPerson | جایگزین مقایسه‌ای |
| CASIA Tampering | جعل تصویر — **نامرتبط** |
| VGGFace2 / CASIA-WebFace | آموزش چهره — خارج scope |

## 1-5. کارهای مرتبط

- Ultralytics documentation و YOLO11 release notes  
- Paper: YOLOv11 Architectural Enhancements (arXiv:2410.17725)  
- ByteTrack: association with low-score detections  
- DeepFace: Serengil et al.  

## 1-6. جمع‌بندی فصل

پایه نظری: YOLO11 anchor-free برای detection، tracker جداگانه برای MOT، DeepFace pretrained برای face ID. فصل بعد روش و ابزار experimental را شرح می‌دهد.
