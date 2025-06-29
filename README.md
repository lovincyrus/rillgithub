# GitHub Commit Downloader

This project provides a script to extract commit and file modification data from a specified GitHub repository and store it as Parquet files in a Google Cloud Storage (GCS) bucket.

## Features

- Downloads all commit metadata and file changes from a GitHub repository using [PyDriller](https://github.com/ishepard/pydriller).
- Stores the data in Parquet format in a specified GCS bucket.
- Supports command-line arguments for repository, bucket path, and GCP credentials.

## Requirements

- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management
- Google Cloud service account with write access to the target GCS bucket

## Setup

1. **Clone the repository**
   ```sh
   git clone <this-repo-url>
   cd <repo-directory>
   ```
2. **Install dependencies**
   ```sh
   poetry install
   ```
3. **Prepare your GCP service account key**
   - Download the JSON key file for a service account with access to your GCS bucket.
   - Place it in the project directory or note its path for use with the script.

## Usage

### Basic usage (with defaults)

This will use the default repository (`rilldata/rill`), default bucket path, and default service account key file:

```sh
poetry run python download_commits.py
```

### Custom arguments

You can specify a different repository, bucket path, or key file:

```sh
poetry run python download_commits.py \
  --repo-slug owner/repo \
  --bucket-path gs://your-bucket/path \
  --gcp-service-account-key-file /path/to/key.json
```

#### Arguments

- `--repo-slug`: GitHub repository in `owner/repo` format (default: `rilldata/rill`)
- `--bucket-path`: GCS bucket path to store Parquet files (default: `gs://rill-github-public/github-analytics/rilldata/rill/commits`)
- `--gcp-service-account-key-file`: Path to GCP service account key file (default: `github-analytics-service-account.json`)

## Output

- Two Parquet files will be written to the specified GCS bucket:
  - `commits_<timestamp>.parquet`: Commit metadata
  - `modified_files_<timestamp>.parquet`: File modification details

## Troubleshooting

- **ModuleNotFoundError**: If you see errors about missing modules (e.g., `pandas`), make sure you have run `poetry install`.
- **Long clone times**: For large repositories, the initial clone by PyDriller may take a while. Be patient, or use a smaller repository for testing.
- **GCP authentication errors**: Ensure your service account key file is valid and has the correct permissions for the target bucket.
- **README or packaging errors**: If Poetry complains about missing README or package elements, you can ignore these if you are not publishing the package, or add a minimal README as shown here.

## FastAPI Endpoint Usage

You can also trigger the GitHub data download via a web API using FastAPI.

### Start the server

```sh
poetry run uvicorn main:app --reload
```

### Endpoint

- **GET** `/generate/{owner}/{repo}`
- Optional query parameters:
  - `bucket_path`: Override the default GCS bucket path
  - `gcp_key`: Override the default GCP service account key file

#### Example URLs

- Default usage:
  - `http://127.0.0.1:8000/generate/rilldata/rill`
- With custom bucket path and GCP key:
  - `http://127.0.0.1:8000/generate/rilldata/rill?bucket_path=gs://your-bucket/path&gcp_key=/path/to/key.json`

#### Example curl command

```sh
curl "http://127.0.0.1:8000/generate/rilldata/rill"
```

```sh
curl "http://127.0.0.1:8000/generate/rilldata/rill?bucket_path=gs://your-bucket/path&gcp_key=/path/to/key.json"
```

The endpoint will return a JSON response indicating the status of the operation.

## Bash Script: Automated Rill Project Generation

You can automate the entire workflow using the provided `generate_rill_project.sh` script.

### What it does

- Runs the commit extraction and uploads the parquet file to GCS.
- Creates a local Rill project structure for the specified GitHub repo.
- Downloads the latest commits parquet file from GCS into the new project directory.
- Changes into the project directory and automatically starts the Rill app.

### Usage

1. Make the script executable:
   ```sh
   chmod +x generate_rill_project.sh
   ```
2. Run the script with your repo slug (and optionally a custom bucket path):
   ```sh
   ./generate_rill_project.sh owner/repo
   # or with a custom bucket path
   ./generate_rill_project.sh owner/repo gs://your-bucket/path
   ```

The script will:

- Extract commit data from the specified repo
- Scaffold a Rill project
- Download the latest parquet file from GCS
- Launch the Rill dashboard automatically in the new project directory
