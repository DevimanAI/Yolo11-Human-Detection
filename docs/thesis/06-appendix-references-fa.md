# پیوست و منابع

## پیوست ۱ — دستور اجرای سریع

```powershell
.\scripts\setup.ps1
.\scripts\setup-train.ps1
.\scripts\download_dataset.ps1
.\.venv\Scripts\python.exe scripts\convert_crowdhuman.py
.\scripts\train_yolo11.ps1
.\.venv\Scripts\python.exe run.py
```

## پیوست ۲ — فایل‌های پیکربندی

- `configs/person_crowdhuman.yaml`  
- `configs/train_yolo11n.yaml`  
- `.env.example`  

## پیوست ۳ — خروجی نمونه smoke test

فایل: `data/sample/bus_detected.jpg`  
تعداد person در bus.jpg: 4 (با yolo11n pretrained)

## پیوست ۴ — نمودارهای آموزش

پس از train: `docs/training_runs/<run>_*/results.png`  
خلاصه JSON: `export_summary.json`

## پیوست ۵ — listing کلیدی detector.py

فراخوانی `model.track` با `classes=[0]`, `persist=True`, tracker yaml.

---

# منابع و مراجع

1. Ultralytics, YOLO11 Documentation, https://docs.ultralytics.com  
2. Ultralytics, yolo11.yaml model definition, https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/11/yolo11.yaml  
3. Jocher et al., Ultralytics YOLO (2023–2024)  
4. Lin et al., Microsoft COCO Dataset, https://cocodataset.org  
5. Shao et al., CrowdHuman Dataset, https://www.crowdhuman.org  
6. Zhang et al., ByteTrack (2022)  
7. Serengil et al., DeepFace Library  
8. YOLOv11 Architectural Enhancements, arXiv:2410.17725  
9. YOLOv8 to YOLO11 Comparative Review, arXiv:2501.13400  
10. FastAPI Documentation, https://fastapi.tiangolo.com  
11. OpenCV Documentation, https://docs.opencv.org  
12. PyTorch Documentation, https://pytorch.org/docs  

---

# فرم‌های کمitee پروژه

فرم‌های انتخاب، تمدید و دفاع طبق پیوست ۱ [فرمت پروژه.pdf](../فرمت%20پروژه.pdf) از دانشکده تهیه و به نسخه چاپی الصاق شوند.
