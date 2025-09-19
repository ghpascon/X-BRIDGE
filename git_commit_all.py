""" 
poetry run python git_commit_all.py 
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def git_commit_all():
    """
    Stage all changes, commit, and push to the current Git repository.
    Asks the user for a commit title and description.
    """
    repo_path = Path.cwd()  # Current directory

    # Ask for commit title
    commit_title = input("Enter commit title (short): ").strip()
    if not commit_title:
        commit_title = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Ask for optional description
    commit_description = input("Enter commit description (optional): ").strip()
    if commit_description:
        commit_message = f"{commit_title}\n\n{commit_description}"
    else:
        commit_message = commit_title

    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        print("Staged all changes.")

        # Commit changes
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        print(f"Committed changes with message:\n{commit_message}")

        # Push to current branch
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("Pushed changes to remote repository.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    git_commit_all()
