from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from dependencies import document_service, embedding_service, vector_store

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/sources")
async def upload_sources(files: list[UploadFile] = File(...)):
    uploaded = []
    
    for file in files:
        try:
            file_path = UPLOAD_DIR / file.filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
                
            text = document_service.load_text(file_path)
            chunks = document_service.chunk_text(text)
            embeddings = embedding_service.get_embeddings(chunks)
            vector_store.add(chunks, embeddings, source=file.filename)
            
            uploaded.append({"name": file.filename})
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
        
    return {"uploaded": uploaded}