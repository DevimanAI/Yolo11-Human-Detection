# راهنمای گالری چهره DeepFace (بدون آموزش CNN از صفر)

## ۱. این لایه چه کاری انجام می‌دهد؟

در پروژه حاضر، **DeepFace** برای **شناسایی** (Identification) استفاده می‌شود، نه آموزش شبکه از ابتدا. مدل **Facenet512** از قبل روی میلیون‌ها چهره آموزش دیده است؛ شما فقط:

1. عکس مرجع هر فرد را در `data/known_faces/<نام>/` قرار می‌دهید؛
2. در زمان راه‌اندازی، embedding هر عکس محاسبه می‌شود؛
3. برای هر crop چهره از ویدئو، فاصله کسینوسی با gallery مقایسه می‌شود.

کد: [`app/face_registry.py`](../app/face_registry.py)

---

## ۲. تفاوت با «آموزش YOLO»

| موضوع | YOLO11 | DeepFace در این پروژه |
|--------|--------|------------------------|
| خروجی | جعبه person | نام فرد یا Unknown |
| آموزش | fine-tune روی CrowdHuman | **پیش‌آموزش‌دیده** + gallery محلی |
| داده | هزاران bbox | ۱–۳ عکس مرجع به ازای هر نفر |
| وابستگی | ultralytics + torch | TensorFlow + deepface (اختیاری) |

**پاسخ دفاع:** «آموزش CNN چهره از صفر به مجموعه‌داده‌ای مثل VGGFace2 یا CASIA-WebFace نیاز دارد که موضوع جدا از تشخیص بدن است؛ ما از transfer learning و embedding gallery استفاده کردیم.»

---

## ۳. نصب

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-face.txt
```

اولین اجرا مدل Facenet512 را دانلود می‌کند (~۱۰۰ مگابایت).

---

## ۴. ساخت گالری

ساختار پوشه:

```
data/known_faces/
  Sara/
    front.jpg
    side.jpg
  Ali/
    photo.png
```

توصیه‌ها:

- چهره رو به دوربین، نور کافی، حداقل ۱۰۰×۱۰۰ پیکسل در crop
- ۱–۳ عکس متنوع به ازای هر نفر
- نام پوشه = برچسب نمایشی در UI

بررسی gallery:

```powershell
.\.venv\Scripts\python.exe scripts\build_face_gallery.py
.\.venv\Scripts\python.exe scripts\build_face_gallery.py --build
```

---

## ۵. تنظیمات `.env`

```ini
FACE_RECOGNITION_ENABLED=true
KNOWN_FACES_DIR=data/known_faces
FACE_MODEL=Facenet512
FACE_MATCH_THRESHOLD=0.4
```

| متغیر | اثر |
|--------|-----|
| `FACE_MATCH_THRESHOLD` | کمتر = سخت‌گیرانه‌تر (کاهش false positive) |
| `FACE_MODEL` | Facenet512 (پیش‌فرض)، VGG-Face، ArcFace و غیره |
| `FACE_RECOGNITION_ENABLED=false` | فقط ردیابی؛ بدون TensorFlow |

---

## ۶. جریان در زمان اجرا

1. YOLO شخص را detect + track می‌کند؛
2. از bbox، crop BGR استخراج می‌شود؛
3. DeepFace embedding crop را می‌سازد؛
4. نزدیک‌ترین embedding در gallery انتخاب می‌شود؛
5. اگر فاصله ≤ آستانه → نام فرد؛ وگرنه `Unknown`.

کش هویت ۲ ثانیه برای هر `track_id` در [`app/pipeline.py`](../app/pipeline.py).

---

## ۷. عیب‌یابی

| مشکل | راه‌حل |
|------|--------|
| همیشه Unknown | عکس بزرگ‌تر؛ آستانه را 0.35 امتحان کنید |
| `No module named 'deepface'` | `requirements-face.txt` نصب نشده |
| کند شدن FPS | `FACE_RECOGNITION_ENABLED=false` یا GPU |
| چهره در crop نیست | شخص دور است؛ YOLO bbox کوچک است |

---

## ۸. گسترش آینده (خارج از scope فعلی)

- fine-tune Facenet روی چهره‌های محلی دانشگاه
- یک کلاس «مهمان» با negative gallery
- ترکیب Re-ID در BoT-SORT برای ردیابی بلندمدت
