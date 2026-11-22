import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from backend.app.retrieval.hybrid_search import hybrid_search

from backend.app.ingestion.repository_manager import clone_repository
from backend.app.retrieval.search_service import search_code

app = FastAPI(
    title="Codebase Onboarding Assistant",
    description="AI-powered codebase understanding and search",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Codebase Onboarding Assistant API is running!"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": "Codebase Onboarding Assistant"
    }


class RepositoryRequest(BaseModel):
    github_url: HttpUrl


@app.post("/api/repositories/clone")
def clone_repo(request: RepositoryRequest):

    try:
        result = clone_repository(str(request.github_url))

        return {
            "success": True,
            "message": "Repository cloned successfully!",
            "data": result
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Repository cloning timed out."
        )

    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error))

    
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    repository: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


@app.post("/api/search")
def semantic_search(request: SearchRequest):

    try:
        results = search_code(
            query=request.query,
            repository=request.repository,
            top_k=request.top_k
        )

        return {
            "success": True,
            "total_results": len(results),
            "results": results
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.post("/api/hybrid-search")
def hybrid_search_endpoint(request: SearchRequest):

    try:
        results = hybrid_search(
            query=request.query,
            repository=request.repository,
            top_k=request.top_k
        )

        return {
            "success": True,
            "total_results": len(results),
            "results": results
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))