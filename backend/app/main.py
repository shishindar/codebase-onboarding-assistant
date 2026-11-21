import subprocess
from pydantic import BaseModel, HttpUrl
from fastapi import HTTPException
from backend.app.ingestion.repository_manager import clone_repository
from fastapi import FastAPI

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
