import logging
import os
import argparse

import pandas as pd
from pydriller import Repository

# Git configurations
# REPO_SLUG = "rilldata/rill"
# REPO_URL = f"https://github.com/{REPO_SLUG}.git"

# Google Cloud configurations
# BUCKET_PATH = f"gs://rilldata-public/github-analytics/{REPO_SLUG}/commits"
# GCP_SERVICE_ACCOUNT_KEY_FILE = "github-analytics-service-account.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def write_list_to_gcs(list, filename, bucket_path, gcp_service_account_key_file):
    # Set the environment variable for the service account key file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_service_account_key_file

    df = pd.DataFrame(list)
    TIMESTAMP = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
    df.to_parquet(f"{bucket_path}/{filename}_{TIMESTAMP}.parquet")
    return


def download_commits(repo_url, bucket_path, gcp_service_account_key_file):
    commits = []
    modified_files = []

    # Traverse the commits in the repository
    for commit in Repository(repo_url).traverse_commits():
        commits.append(
            {
                "commit_hash": commit.hash,
                "commit_msg": commit.msg,
                "author_name": commit.author.name,
                "author_email": commit.author.email,
                "author_date": commit.author_date,
                "author_timezone": commit.author_timezone,
                "merge": commit.merge,
            }
        )

        # Iterate over the modified files in each commit
        for modified_file in commit.modified_files:
            modified_files.append(
                {
                    "commit_hash": commit.hash,
                    "filename": modified_file.filename,
                    "old_path": modified_file.old_path,
                    "new_path": modified_file.new_path,
                    "added_lines": modified_file.added_lines,
                    "deleted_lines": modified_file.deleted_lines,
                }
            )

    # Write the commits and modified files to GCS
    write_list_to_gcs(commits, "commits", bucket_path, gcp_service_account_key_file)
    write_list_to_gcs(modified_files, "modified_files", bucket_path, gcp_service_account_key_file)

    # done
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download GitHub repo commits and upload to GCS.")
    parser.add_argument(
        "--repo-slug",
        type=str,
        default="rilldata/rill",
        help="GitHub repository slug (e.g., owner/repo)",
    )
    parser.add_argument(
        "--bucket-path",
        type=str,
        default="gs://rilldata-public/github-analytics/rilldata/rill/commits",
        help="GCS bucket path to store parquet files",
    )
    parser.add_argument(
        "--gcp-service-account-key-file",
        type=str,
        default="github-analytics-service-account.json",
        help="Path to GCP service account key file",
    )
    args = parser.parse_args()

    repo_url = f"https://github.com/{args.repo_slug}.git"
    download_commits(repo_url, args.bucket_path, args.gcp_service_account_key_file)
