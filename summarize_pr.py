import subprocess
import os
import requests
from pydantic import BaseModel
from typing import List

class PRSummary(BaseModel):
    high_level_summary: List[str]
    potential_breaking_changes: List[str]
    recommended_code_improvements: List[str]

def get_git_diff():
    result = subprocess.run(
        ['git', 'diff', 'origin/main...HEAD'],
        stdout=subprocess.PIPE,
        text=True
    )
    return result.stdout

def analyze_diff(diff_text: str) -> PRSummary:
    # Placeholder for actual analysis logic
    # Replace this with your Pydantic-based agent implementation
    return PRSummary(
        high_level_summary=["Updated deployment workflow."],
        potential_breaking_changes=["Changed trigger from push to pull_request."],
        recommended_code_improvements=["Consider pinning action versions."]
    )

def post_comment(pr_number: int, comment_body: str):
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
        print("Comment posted successfully.")
    else:
        print(f"Failed to post comment: {response.status_code}")

def main():
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

    # Extract PR number from environment variable
    pr_number = os.environ.get('PR_NUMBER')
    if pr_number:
        post_comment(int(pr_number), comment)
    else:
        print("PR_NUMBER environment variable not set.")

if __name__ == "__main__":
    main()