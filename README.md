# SelfRAG

SelfRAG is a modern, document-based Retrieval-Augmented Generation (RAG) platform that enables users to upload documents (such as PDFs) and perform natural language queries over their content. The system leverages advanced chunking, embedding, vector search, and reranking techniques to provide accurate, context-aware answers.

---

## Features

- **Document Upload & Query:** Upload PDF documents and ask questions in natural language.
- **RAG Architecture:** Combines retrieval and generation for reliable, up-to-date answers.
- **Chunking & Embedding:** Splits documents into chunks and generates vector representations for efficient search.
- **Advanced Search:** FAISS-based vector search and reranking for high-quality results.
- **User Management:** Registration, login, and profile management.
- **Modern UI:** User-friendly React-based web interface.

---

## Installation

### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # (Windows) or source venv/bin/activate (Linux/Mac)
pip install -r ../requirements.txt
```

#### Run the Backend

```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```
> Note: Use `backend/main.py` or `backend/api/main.py` as your entry point if needed.

### 2. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

### 3. Environment Variables

If required, define environment variables in a `.env` file.

---

## Usage

1. Access the web interface via your browser (e.g., `http://localhost:5173`).
2. Register or log in.
3. Upload your documents.
4. Ask questions in natural language and view the answers.

---

## Architecture

SelfRAG consists of two main components:

- **Backend (Python, FastAPI):**
  - Handles document reading, chunking, embedding, vector search (FAISS), reranking, user management, and API services.
- **Frontend (React):**
  - Provides the user interface, session management, document upload, and query screens.

### Flow Diagram

```mermaid
graph TD
A[User] --> B[Frontend (React)]
B --> C[Backend (FastAPI)]
C --> D[Document Reading & Chunking]
D --> E[Embedding & Vector Search (FAISS)]
E --> F[Reranker]
F --> G[Answer Generation (Generator)]
G --> B
```

---