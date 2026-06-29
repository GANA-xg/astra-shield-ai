from pathlib import Path
import shutil

from fastapi import APIRouter, File, UploadFile

from agents.currency_agent.service import analyze_currency

router = APIRouter(
    prefix="/currency",
    tags=["Currency Detection"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_currency(str(file_path))

    return result