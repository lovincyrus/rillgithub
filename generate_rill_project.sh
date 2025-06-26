#!/bin/bash

# Usage: ./generate_rill_project.sh owner/repo [bucket_path]
# Example: ./generate_rill_project.sh rilldata/rill gs://rilldata-public/github-analytics/rilldata/rill/commits

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 owner/repo [bucket_path]"
  exit 1
fi

REPO_SLUG="$1"
SOURCE_NAME=$(echo "$REPO_SLUG" | tr '/' '_')
PROJECT_NAME="${SOURCE_NAME}_rill"
BUCKET_PATH="${2:-gs://rilldata-public/github-analytics/$REPO_SLUG/commits}"

# 1. Download commits (uploads parquet to GCS)
poetry run python download_commits.py --repo-slug "$REPO_SLUG" --bucket-path "$BUCKET_PATH"

# 2. Create the Rill project structure
poetry run python create_local_rill_project.py --repo-slug "$REPO_SLUG"

# 3. Download the latest commits parquet file from GCS into the new project directory
LATEST_PARQUET=$(gsutil ls "$BUCKET_PATH/commits_*.parquet" | sort | tail -n 1)
gsutil cp "$LATEST_PARQUET" "${PROJECT_NAME}/commits.parquet"

# 4. Start Rill in the project directory
cd "$PROJECT_NAME"
rill start 