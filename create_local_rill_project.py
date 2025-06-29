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
connector: "gcs"
uri: "gs://rill-github-public/github-analytics/{repo_slug}/commits/commits*.parquet"
# Workaround for caching problem
extract:
  files:
    strategy: tail
    size: 1
''',
    "sources/{source_name}_modified_files.yaml": '''
type: source
connector: "gcs"
uri: "gs://rill-github-public/github-analytics/{repo_slug}/commits/modified_files*.parquet"
# Workaround for caching problem
extract:
  files:
    strategy: tail
    size: 1
''',
    "models/{source_name}_commits_model.sql": '''
SELECT
    author_date AS date,
    c.commit_hash,
    commit_msg AS commit_message,
    author_name AS username,
    merge AS is_merge_commit,
    new_path AS file_path,
    filename,
    RIGHT(filename, POSITION('.' IN REVERSE(filename))) AS file_extension,
    CASE WHEN CONTAINS(file_path, '/')
      THEN SPLIT_PART(file_path, '/', 1)
      ELSE NULL
    END AS first_directory,
    CASE WHEN CONTAINS(SUBSTRING(file_path, LENGTH(first_directory) + 2), '/')
      THEN SPLIT_PART(file_path, '/', 2)
      ELSE NULL
    END AS second_directory,
    CASE 
      WHEN first_directory IS NOT NULL AND second_directory IS NOT NULL
        THEN CONCAT(first_directory, '/', second_directory) 
      WHEN first_directory IS NOT NULL
        THEN first_directory
      WHEN first_directory IS NULL
        THEN NULL
    END AS second_directory_concat,
    added_lines AS additions,
    deleted_lines AS deletions, 
    additions + deletions AS changes, 
    old_path AS previous_file_path
FROM {source_name}_commits_source c
LEFT JOIN {source_name}_modified_files f ON c.commit_hash = f.commit_hash
''',
    "metrics/{source_name}_commits_metrics.yaml": '''
version: 1
type: metrics_view

display_name: {project_title} Commits Model Metrics
model: {source_name}_commits_model
timeseries: date
smallest_time_grain: "day"

dimensions:
  - name: commit_hash
    display_name: Commit hash
    expression: commit_hash
    description: ""
  - name: commit_message
    display_name: Commit message
    expression: commit_message
    description: ""
  - name: username
    display_name: Username
    expression: username
    description: ""
  - name: file_path
    display_name: File path
    expression: file_path
    description: ""
  - name: filename
    display_name: Filename
    expression: filename
    description: ""
  - name: file_extension
    display_name: File extension
    expression: file_extension
    description: ""
  - name: first_directory
    display_name: First directory
    expression: first_directory
    description: ""
  - name: second_directory
    display_name: Second directory
    expression: second_directory_concat
    description: ""
  - name: previous_file_path
    display_name: Previous file path
    expression: previous_file_path
    description: ""
  - name: is_merge_commit
    display_name: Merge commit
    expression: is_merge_commit
    description: "True if the commit is a merge commit"

measures:
  - display_name: "Number of commits"
    expression: "count(distinct commit_hash)"
    name: number_of_commits
    description: ""
    format_preset: humanize
  - display_name: Number of files touched
    expression: count(distinct filename)
    name: count_of_distinct_filename
    description: ""
    format_preset: humanize
  - display_name: "Number of contributors"
    expression: "count(distinct username)"
    name: count_of_distinct_username
    description: ""
    format_preset: humanize
  - display_name: "Code additions"
    expression: "sum(additions)"
    name: sum_of_additions
    description: ""
    format_preset: humanize
  - display_name: "Code deletions"
    expression: "sum(deletions)"
    name: sum_of_deletions
    description: ""
    format_preset: humanize
  - display_name: "Code changes"
    expression: "sum(changes)"
    name: sum_of_changes
    description: ""
    format_preset: humanize
  - display_name: "Code deletion %"
    expression: "sum(deletions) / sum(changes)"
    name: percent_code_change
    description: "The percentage of code changes that were deletions."
    format_preset: percentage
  - display_name: "Files touched per commit"
    expression: "count(*) / count(distinct commit_hash)"
    name: count_files_touched_per_commit
    description: ""
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