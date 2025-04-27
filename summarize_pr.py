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
    """Find old bot comment (if any), delete it, then post a fresh one."""
    token = os.environ['GITHUB_TOKEN']
    repo = os.environ['GITHUB_REPOSITORY']
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Fetch existing PR comments
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    response = requests.get(comments_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch comments: {response.status_code} - {response.text}")
        return

    comments = response.json()

    # Look for a previous comment made by this bot (tagged with hidden marker)
    bot_comment_id = None
    for comment in comments:
        if "<!--summit-agent-->" in comment['body']:
            bot_comment_id = comment['id']
            break

    if bot_comment_id:
        # Delete the previous comment
        delete_url = f"https://api.github.com/repos/{repo}/issues/comments/{bot_comment_id}"
        delete_response = requests.delete(delete_url, headers=headers)
        if delete_response.status_code == 204:
            print("🧹 Deleted old bot comment.")
        else:
            print(f"❌ Failed to delete old comment: {delete_response.status_code} - {delete_response.text}")

    # Post the new comment
    post_data = {'body': comment_body}
    post_response = requests.post(comments_url, headers=headers, json=post_data)
    if post_response.status_code == 201:
        print("✅ Successfully posted new PR comment.")
    else:
        print(f"❌ Failed to post new comment: {post_response.status_code} - {post_response.text}")
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
        "<!--summit-agent-->\n"  # 🔥 Hidden marker at top
        "## 📝 High-Level Summary\n"
        "<details><summary>Expand</summary>\n\n"
        + "\n".join(f"- {item}" for item in summary.high_level_summary)
        + "\n</details>\n\n"
        "## ⚠️ Potential Breaking Changes\n"
        "<details><summary>Expand</summary>\n\n"
        + "\n".join(f"- {item}" for item in summary.potential_breaking_changes)
        + "\n</details>\n\n"
        "## ✅ Recommended Code Improvements\n"
        "<details><summary>Expand</summary>\n\n"
        + "\n".join(f"- {item}" for item in summary.recommended_code_improvements)
        + "\n</details>"
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