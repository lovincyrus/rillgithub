from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from download_commits import download_commits
import os

app = FastAPI()

# Default values (should match those in download_commits.py)
DEFAULT_BUCKET_PATH = "gs://rilldata-public/github-analytics/rilldata/rill/commits"
DEFAULT_GCP_KEY = "github-analytics-service-account.json"

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
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=500) 