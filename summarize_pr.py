import os
import subprocess
import requests
import asyncio
from typing import List

from pydantic import BaseModel
from pydantic_ai import Agent

# -------------------
# Define your output structure
# -------------------
class PRSummary(BaseModel):
    high_level_summary: List[str]
    potential_breaking_changes: List[str]
    recommended_code_improvements: List[str]

# -------------------
# Set up the Agent
# -------------------
agent = Agent(
    model="openai:gpt-4o",  # Change this if you're using another model
    result_type=PRSummary,
    system_prompt="""
You are a GitHub Pull Request Summarization Assistant.

Given a Git diff, you must:
- Summarize high-level changes (short bullet points)
- Identify any possible breaking changes
- Recommend improvements or best practices

Always output strictly matching this schema:
{
  "high_level_summary": ["..."],
  "potential_breaking_changes": ["..."],
  "recommended_code_improvements": ["..."]
}
"""
)

# -------------------
# Functions
# -------------------
def get_git_diff() -> str:
    """Get the diff between the main branch and the current HEAD."""
    result = subprocess.run(
        ['git', 'diff', 'origin/main...HEAD'],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout

async def analyze_diff(diff_text: str) -> PRSummary:
    """Call the real agent on the diff."""
    result = await agent.run(diff_text)
    return result.output

def post_comment(pr_number: str, comment_body: str):
    """Post a comment to the PR."""
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

# -------------------
# Main Runner
# -------------------
def main():
    print("🚀 Starting PR Summarizer...")
    diff = get_git_diff()

    # Analyze asynchronously
    summary = asyncio.run(analyze_diff(diff))

    # Format nice comment markdown
    comment = (
        "## 📝 High-Level Summary\n"
        + "\n".join(f"- {item}" for item in summary.high_level_summary)
        + "\n\n## ⚠️ Potential Breaking Changes\n"
        + "\n".join(f"- {item}" for item in summary.potential_breaking_changes)
        + "\n\n## ✅ Recommended Code Improvements\n"
        + "\n".join(f"- {item}" for item in summary.recommended_code_improvements)
    )

    # Detect PR number from GitHub env
    github_ref = os.environ.get('GITHUB_REF', '')
    pr_number = None
    if github_ref.startswith('refs/pull/'):
        pr_number = github_ref.split('/')[2]

    if pr_number:
        post_comment(pr_number, comment)
    else:
        print(f"❌ PR number not found in GITHUB_REF: {github_ref}")

if __name__ == "__main__":
    main()