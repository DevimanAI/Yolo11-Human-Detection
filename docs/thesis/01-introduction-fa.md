# مقدمه

## 1-1. بیان مسئله

رشد کاربردهای نظارت ویدئویی، کنترل تردد و تحلیل رفتار جمعیت نیازمند سیستمی است که بتواند **انسان** را در هر فریم تصویر بیابد، در فریم‌های بعدی **همان فرد** را با شناسه پایدار دنبال کند و در صورت نیاز **هویت چهره** را با پایگاه مرجع مقایسه نماید. روش‌های سنتی مبتنی بر پردازش دستی یا detectorهای کند برای پردازش بلادرنگ مناسب نیستند.

خانواده **YOLO** با philosophy «یک بار نگاه کن» (single-stage) تعادل مناسبی بین دقت و سرعت ارائه داده و در نسخه‌های اخیر Ultralytics—including **YOLO11**—بهبود معماری C3k2، SPPF و C2PSA را شامل می‌شود.

## 1-2. اهداف پروژه

1. پیاده‌سازی pipeline تشخیص person با YOLO11n  
2. افزودن ردیابی ByteTrack/BoT-SORT برای Track ID پایدار  
3. لایه اختیاری شناسایی چهره با DeepFace  
4. رابط وب FastAPI برای نمایش زنده  
5. **آموزش و fine-tune** مدل روی مجموعه person (CrowdHuman)  
6. مستندسازی کامل hyperparameterها برای دفاع دانشگاهی  

## 1-3. محدوده و خارج از scope

- **داخل scope:** detection + tracking + gallery چهره + fine-tune YOLO  
- **خارج scope:** آموزش CNN چهره از صفر؛ تشخیص دستکاری تصویر (CASIA Tampering)  

## 1-4. چرا CASIA Tampering انتخاب نشد؟

استاد مجموعه [CASIA 2.0 Image Tampering](https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset) را پیشنهاد کرده بود. بررسی نشان داد این داده برای **localization ناحیه جعل** است و برچسب person bounding box ندارد. هم‌راستایی مسئله–داده (problem–dataset alignment) اصل اول انتخاب مجموعه است؛ hence **CrowdHuman** برای fine-tune YOLO انتخاب شد.

## 1-5. ساختار پایان‌نامه

- **فصل ۱:** مرور ادبیات YOLO، MOT، DeepFace  
- **فصل ۲:** روش تحقیق، ابزار، مجموعه‌داده، معیارها  
- **فصل ۳:** پیاده‌سازی، آموزش، نتایج  
- **فصل ۴:** بحث، نتیجه‌گیری، پیشنهادات  

## 1-6. نوآوری و ارزش افزوده

ترکیب end-to-end: pretrained YOLO11 + tracker + DeepFace gallery + اسکریپت آموزش reproducible + مستند فارسی hyperparameter برای دفاع؛ مناسب پروژه کارشناسی مهندسی کامپیوتر.
