from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from download_commits import download_commits
import os
import logging
from git.exc import GitCommandError

app = FastAPI()

# Default values (should match those in download_commits.py)
DEFAULT_BUCKET_PATH = "gs://rill-github-public/github-analytics/rilldata/rill/commits"
DEFAULT_GCP_KEY = "github-analytics-service-account.json"

# Configure logging for the API
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

@app.get("/generate/{owner}/{repo}")
def generate(owner: str, repo: str, bucket_path: str = Query(None), gcp_key: str = Query(None)):
    repo_slug = f"{owner}/{repo}"
    repo_url = f"https://github.com/{repo_slug}.git"
    bucket_path = bucket_path or DEFAULT_BUCKET_PATH
    gcp_key = gcp_key or DEFAULT_GCP_KEY
    try:
        download_commits(repo_url, bucket_path, gcp_key)
        return JSONResponse({
            "status": "success",
            "repo": repo_slug,
            "bucket_path": bucket_path
        })
    except GitCommandError as e:
        logger.error(f"Git error for repo {repo_slug}: {e}")
        return JSONResponse({
            "status": "error",
            "error": "Repository not found or inaccessible.",
            "details": str(e)
        }, status_code=404)
    except Exception as e:
        logger.error(f"Unexpected error for repo {repo_slug}: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=500) 