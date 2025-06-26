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

This will use the default repository (`duckdb/duckdb`), default bucket path, and default service account key file:

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

- `--repo-slug`: GitHub repository in `owner/repo` format (default: `duckdb/duckdb`)
- `--bucket-path`: GCS bucket path to store Parquet files (default: `gs://rilldata-public/github-analytics/duckdb/duckdb/commits`)
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
