from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Tuple
import os
import sys
from pathlib import Path
import time
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
import base64

from backend.reader.pdf_reader import PDFReader

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.models import QueryRequest, QueryResponse, DocumentResponse
from backend.api.dependencies import get_rag_system
from backend.core.rag_system import RAGSystem
from backend.api.auth import router as auth_router, get_current_user

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

app.include_router(auth_router)

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "selfRAG")
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
queries_collection = db["queries"]

BACKEND_DIR = Path(__file__).parent.parent

@app.get("/")
async def root():
    return {"message": "AskMyDocs API is running!"}

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    rag_system: RAGSystem = Depends(get_rag_system),
    current_user=Depends(get_current_user)
):
    """
    Process a query using Self-RAG
    """
    import time as t
    start = t.time()
    try:
        result = await rag_system.process_query(
            query=request.query,
            top_k=request.top_k,
            use_self_rag=request.use_self_rag,
        )
        duration = t.time() - start
        # Save query analytics
        self_rag_info = result.get("self_rag_info")
        query_doc = {
            "query": request.query,
            "processing_time": duration,
            "self_rag_score": self_rag_info["final_score"] if self_rag_info and "final_score" in self_rag_info else None,
            "created_at": datetime.utcnow(),
            "username": current_user["username"]
        }
        await queries_collection.insert_one(query_doc)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...), current_user=Depends(get_current_user)):
    """
    Upload and process documents (admin only)
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Only admin users can upload documents.")
    try:
        uploaded_files = []
        data_dir = BACKEND_DIR / "data"
        data_dir.mkdir(exist_ok=True)
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(400, "Only PDF files are supported")
            # Save file
            file_path = data_dir / file.filename
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
        data_dir = BACKEND_DIR / "data"
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
async def delete_document(filename: str, current_user=Depends(get_current_user)):
    """
    Delete a document (admin only)
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Only admin users can delete documents.")
    try:
        data_dir = BACKEND_DIR / "data"
        file_path = data_dir / filename
        if not file_path.exists():
            raise HTTPException(404, "File not found")
        file_path.unlink()
        # Trigger index rebuild
        rag_system = get_rag_system()
        await rag_system.rebuild_index()
        return {"message": f"Deleted {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# --- Analytics Endpoint ---
@app.get("/api/analytics/queries")
async def get_query_analytics(current_user=Depends(get_current_user)):
    cursor = queries_collection.find({"username": current_user["username"]}).sort("created_at", -1)
    queries = await cursor.to_list(length=100)
    total_queries = await queries_collection.count_documents({"username": current_user["username"]})
    if queries:
        avg_processing_time = sum(q.get("processing_time", 0) for q in queries) / len(queries)
        avg_self_rag_score = sum(q.get("self_rag_score", 0) for q in queries if q.get("self_rag_score") is not None) / max(1, sum(1 for q in queries if q.get("self_rag_score") is not None))
    else:
        avg_processing_time = 0
        avg_self_rag_score = 0
    recent_queries = [
        {
            "query": q["query"],
            "processing_time": q.get("processing_time", 0),
            "self_rag_score": q.get("self_rag_score"),
            "created_at": q["created_at"].isoformat() if q.get("created_at") else None
        }
        for q in queries[:10]
    ]
    return {
        "total_queries": total_queries,
        "avg_processing_time": avg_processing_time,
        "avg_self_rag_score": avg_self_rag_score,
        "recent_queries": recent_queries
    }

# --- System Status Endpoint ---
@app.get("/api/system/status")
async def get_system_status():
    data_dir = BACKEND_DIR / "data"
    pdf_files = list(data_dir.glob("*.pdf"))
    rag_system = get_rag_system()
    chunk_count = len(getattr(rag_system.vectorstore, "documents", []))
    return {
        "status": "ok",
        "vectorstore": {
            "has_documents": len(pdf_files) > 0,
            "document_count": len(pdf_files),
            "chunk_count": chunk_count,
            "index_ready": True
        },
        "data_directory": {
            "path": str(data_dir.resolve()),
            "exists": data_dir.exists(),
            "pdf_count": len(pdf_files),
            "pdf_files": [f.name for f in pdf_files]
        },
        "components": {
            "reader": True,
            "chunker": True,
            "embedder": True,
            "generator": True,
            "reranker": True
        }
    }

# --- Rebuild Index Endpoint ---
@app.post("/api/system/rebuild-index")
async def rebuild_index(background_tasks: BackgroundTasks):
    data_dir = BACKEND_DIR / "data"
    rag_system = get_rag_system()
    background_tasks.add_task(rag_system.rebuild_index)
    pdf_files = list(data_dir.glob("*.pdf"))
    return {
        "message": "Index rebuild started",
        "document_count": len(pdf_files),
        "status": "rebuilding"
    }
    
@app.get("/api/documents/{filename}/pages")
async def get_pdf_pages(filename: str):
    """
    Return the text content of each page in the given PDF file.
    """
    data_dir = BACKEND_DIR / "data"
    file_path = data_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    reader = PDFReader()
    try:
        pages = reader.read(str(file_path))  # List[Tuple[int, str]]
        return [{"page": page_num, "text": text} for page_num, text in pages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {e}")
    
@app.get("/api/documents/{filename}/download")
async def download_pdf(filename: str):
    """
    Download the original PDF file.
    """
    data_dir = BACKEND_DIR / "data"
    file_path = data_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), media_type="application/pdf", filename=filename)
    
@app.get("/api/documents/{filename}/base64")
async def get_pdf_base64(filename: str):
    """
    Return the PDF file as a base64-encoded string.
    """
    data_dir = BACKEND_DIR / "data"
    file_path = data_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return {"filename": filename, "content": encoded}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    