import os
import argparse

PROJECT_TEMPLATE = {
    "rill.yaml": '''
compiler: rillv1

display_name: GitHub Analytics
description: "Rill analytics project for {repo_slug}"
''',
    "sources/{source_name}_commits_source.yaml": '''
type: source
connector: "file"
uri: "commits.parquet"
''',
    "models/{source_name}_commits_model.sql": '''
SELECT
    commit_hash,
    commit_msg AS commit_message,
    author_name,
    author_email,
    author_date,
    author_timezone,
    merge AS is_merge_commit
FROM {source_name}_commits_source
''',
    "metrics/{source_name}_commits_metrics.yaml": '''
version: 1
type: metrics_view
display_name: {project_title} Commits Metrics
model: {source_name}_commits_model
timeseries: author_date
dimensions:
  - name: commit_hash
    display_name: Commit hash
    expression: commit_hash
  - name: commit_message
    display_name: Commit message
    expression: commit_message
  - name: author_name
    display_name: Author
    expression: author_name
  - name: author_email
    display_name: Author Email
    expression: author_email
  - name: is_merge_commit
    display_name: Merge commit
    expression: is_merge_commit
measures:
  - display_name: "Number of commits"
    expression: "count(distinct commit_hash)"
    name: number_of_commits
    format_preset: humanize
''',
    "dashboards/{source_name}_commits_dashboard.yaml": '''
type: explore

display_name: "{project_title} Commits"
metrics_view: {source_name}_commits_metrics

dimensions: '*'
measures: '*'
defaults:
  measures:
    - number_of_commits
    - count_of_distinct_filename
    - count_of_distinct_username
    - sum_of_additions
    - sum_of_deletions
    - sum_of_changes
    - percent_code_change
    - count_files_touched_per_commit
  dimensions:
    - commit_hash
    - commit_message
    - username
    - file_path
    - filename
    - file_extension
    - first_directory
    - second_directory
    - previous_file_path
    - is_merge_commit
  time_range: P12M
''',
}

def create_project_structure(base_dir, files):
    for rel_path, content in files.items():
        file_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Create a local Rill project for a GitHub repo.")
    parser.add_argument("--repo-slug", required=True, help="GitHub repo slug, e.g. duckdb/duckdb")
    args = parser.parse_args()

    repo_slug = args.repo_slug.strip()
    source_name = repo_slug.replace("/", "_")
    project_name = f"{source_name}_rill"
    project_title = repo_slug.replace("/", " ").title()

    print(f"Creating Rill project: {project_name}")
    files = {k.format(source_name=source_name, project_name=project_name, project_title=project_title, repo_slug=repo_slug): v.format(source_name=source_name, project_name=project_name, project_title=project_title, repo_slug=repo_slug) for k, v in PROJECT_TEMPLATE.items()}
    os.makedirs(project_name, exist_ok=True)
    create_project_structure(project_name, files)

    print(f"\nProject '{project_name}' created!")
    print("\nNext steps:")
    print("1. Run your commit extraction script (e.g., download_commits.py) in this directory to generate 'commits.parquet'.")
    print("2. Run 'rill start' inside the project directory to launch the local Rill app.")
    print("3. Explore your dashboard at http://localhost:9009 (default Rill port).\n")
    print(f"Project files are in: {os.path.abspath(project_name)}")

if __name__ == "__main__":
    main() 