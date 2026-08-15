from pathlib import Path
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/sources")
async def upload_sources(files: list[UploadFile] = File(...)):
    uploaded = []
    
    for file in files:
        file_path = UPLOAD_DIR / file.filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        uploaded.append({"name": file.filename})
        
    return {"uploaded": uploaded}