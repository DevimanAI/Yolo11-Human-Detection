from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.config import settings
from app.pipeline import VideoPipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YOLO Human Detection & Tracking",
    description="Ultralytics YOLO person detection with ByteTrack/BoT-SORT and optional face recognition.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

pipeline = VideoPipeline(settings)


class SourceUpdate(BaseModel):
    source: str = Field(..., description="Webcam index (0), video file path, or stream URL")


@app.on_event("shutdown")
def shutdown_event() -> None:
    pipeline.stop()
    pipeline.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"settings": settings},
    )


@app.get("/api/status")
async def status() -> dict:
    return pipeline.get_status()


@app.post("/api/source")
async def update_source(payload: SourceUpdate) -> dict:
    try:
        source: int | str = int(payload.source) if payload.source.isdigit() else payload.source
        pipeline.stop()
        pipeline.open_source(source)
        return {"ok": True, "source": payload.source}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/video")
async def video_feed() -> StreamingResponse:
    def generate():
        pipeline.stop()
        try:
            pipeline.open_source()
            yield from pipeline.mjpeg_stream()
        except Exception as exc:  # noqa: BLE001
            logger.error("Stream error: %s", exc)
            raise

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
