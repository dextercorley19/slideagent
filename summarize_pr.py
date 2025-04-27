import os
import subprocess
import requests
from pydantic import BaseModel
from typing import List

class PRSummary(BaseModel):
    high_level_summary: List[str]
    potential_breaking_changes: List[str]
    recommended_code_improvements: List[str]

def get_git_diff() -> str:
    """Get diff between main branch and current HEAD."""
    result = subprocess.run(
        ['git', 'diff', 'origin/main...HEAD'],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout

def analyze_diff(diff_text: str) -> PRSummary:
    """Stub analyzer — replace with your real LLM agent."""
    return PRSummary(
        high_level_summary=["Example change detected."],
        potential_breaking_changes=["None detected."],
        recommended_code_improvements=["Consider pinning action versions."]
    )

def post_comment(pr_number: str, comment_body: str):
    """Post a comment to the GitHub Pull Request."""
    token = os.environ['GITHUB_TOKEN']
    repo = os.environ['GITHUB_REPOSITORY']
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {'body': comment_body}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("✅ Successfully posted comment.")
    else:
        print(f"❌ Failed to post comment: {response.status_code} - {response.text}")

def main():
    print("Running PR summarizer...")
    diff = get_git_diff()

    summary = analyze_diff(diff)

    comment = (
        "## 📝 High-Level Summary\n"
        + "\n".join(f"- {item}" for item in summary.high_level_summary)
        + "\n\n## ⚠️ Potential Breaking Changes\n"
        + "\n".join(f"- {item}" for item in summary.potential_breaking_changes)
        + "\n\n## ✅ Recommended Code Improvements\n"
        + "\n".join(f"- {item}" for item in summary.recommended_code_improvements)
    )

    github_ref = os.environ.get('GITHUB_REF', '')
    pr_number = None
    if github_ref.startswith('refs/pull/'):
        # refs/pull/{pr_number}/merge
        pr_number = github_ref.split('/')[2]

    if pr_number:
        post_comment(pr_number, comment)
    else:
        print("❌ PR number not found from GITHUB_REF:", github_ref)

if __name__ == "__main__":
    main()