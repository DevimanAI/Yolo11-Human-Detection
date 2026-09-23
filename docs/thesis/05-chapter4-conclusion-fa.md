# فصل ۴ — بحث، نتیجه‌گیری و پیشنهادات

## 4-1. بحث نتایج

### 4-1-1. تشخیص

YOLO11n با pretrain COCO از قبل person را در smoke test و demo تشخیص می‌دهد. Fine-tune روی CrowdHuman باید mAP را روی صحنه شلوغ و occlusion بهبود دهد—به‌ویژه recall برای افراد کوچک.

### 4-1-2. ردیابی

ByteTrack بدون آموزش اضافه Track ID پایدار می‌دهد. کیفیت tracking به confidence detector و frame rate وابسته است.

### 4-1-3. چهره

DeepFace بدون gallery فقط Unknown برمی‌گرداند. با 1–3 عکس مرجع و `requirements-face.txt` شناسایی فعال می‌شود. آموزش CNN چهره از صفر scope پروژه نبود.

## 4-2. مقایسه با اهداف اولیه

| هدف | وضعیت |
|-----|--------|
| YOLO person detection | تحقق یافته |
| MOT | تحقق یافته |
| Face ID اختیاری | تحقق یافته |
| رابط وب | تحقق یافته |
| Dataset + Train | CrowdHuman + اسکریپت train |
| مستند hyperparameter | training-reference.md |

## 4-3. محدودیت‌ها

1. آموزش کامل CrowdHuman به GPU و زمان نیاز دارد  
2. DeepFace سنگین (TensorFlow) — اختیاری  
3. MJPEG single-client  
4. شناسایی چهره روی crop بدن — نه crop تنگ چهره  
5. CASIA Tampering برای این task مناسب نبود  

## 4-4. نتیجه‌گیری

پروژه یک pipeline عملی برای **تشخیص و ردیابی انسان** با YOLO11 و لایه اختیاری **DeepFace** ارائه کرد. معماری YOLO11 **anchor-free** است؛ hyperparameterهای Ultralytics مستند شدند. مجموعه CrowdHuman جایگزین CASIA گردید. اسکریپت‌های setup/train/export reproducibility را برای گزارش دانشگاهی فراهم می‌کنند.

## 4-5. پیشنهادات آینده

- آموزش روی ویدئوهای محلی دانشگاه  
- TensorRT / ONNX برای FPS بالاتر  
- one-to-many Re-ID در BoT-SORT  
- edge deployment (Raspberry Pi / Jetson)  
- dashboard تحلili رفتار جمعیت  

## 4-6. تجربه شخصی

کار با `.venv` روی Windows، اجتناب از Store Python، و تفکیک inference/train/deepface dependencies درک عملی MLOps را تقویت کرد.
