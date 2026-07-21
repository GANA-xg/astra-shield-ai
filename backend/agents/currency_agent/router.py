from pathlib import Path
import shutil

from fastapi import APIRouter, File, Query, UploadFile

from agents.currency_agent.service import analyze_currency

router = APIRouter(
    prefix="/currency",
    tags=["Currency Detection"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    include_gradcam: bool = Query(False, description="Include Grad-CAM heatmap overlay"),
):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = analyze_currency(str(file_path), include_gradcam=include_gradcam)
        return result
    finally:
        if file_path.exists():
            file_path.unlink()
