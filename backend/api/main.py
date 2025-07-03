from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.models import QueryRequest, QueryResponse, DocumentResponse
from backend.api.dependencies import get_rag_system
from backend.core.rag_system import RAGSystem

app = FastAPI(
    title="AskMyDocs API",
    description="Self-RAG powered document Q&A system",
    version="1.0.0",
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AskMyDocs API is running!"}

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """
    Process a query using Self-RAG
    """
    try:
        result = await rag_system.process_query(
            query=request.query,
            top_k=request.top_k,
            use_self_rag=request.use_self_rag,
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process documents
    """
    try:
        uploaded_files = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(400, "Only PDF files are supported")
            
            # Save file
            file_path = f"data/{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append(file.filename)
        
        # Trigger index rebuild
        rag_system = get_rag_system()
        await rag_system.rebuild_index()
        
        return {"message": f"Uploaded {len(uploaded_files)} files", "files": uploaded_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/documents", response_model=List[DocumentResponse])
async def list_documents():
    """
    List all processed documents
    """
    try:
        data_dir = Path("data")
        documents = []
        for file_path in data_dir.glob("*.pdf"):
            stat = file_path.stat()
            documents.append(DocumentResponse(
                filename=file_path.name,
                size=stat.st_size,
                uploaded_at=stat.st_mtime
            ))
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document
    """
    try:
        file_path = Path(f"data/{filename}")
        if not file_path.exists():
            raise HTTPException(404, "File not found")
        
        file_path.unlink()
        
        # Trigger index rebuild
        rag_system = get_rag_system()
        await rag_system.rebuild_index()
        
        return {"message": f"Deleted {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    