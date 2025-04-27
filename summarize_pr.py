import os
import subprocess
import requests
import asyncio
from typing import List
import json
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
        "<!--summit-agent-->\n"
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

    github_event_name = os.environ.get('GITHUB_EVENT_NAME', '')
    github_event_path = os.environ.get('GITHUB_EVENT_PATH', '')
    github_sha = os.environ.get('GITHUB_SHA', '')

    print(f"🔎 Event: {github_event_name}")

    if github_event_name == 'pull_request_target':
        with open(github_event_path, 'r') as f:
            event_data = json.load(f)
            pr_number = event_data.get('number')

        if pr_number:
            print(f"📦 Detected PR #{pr_number}. Posting comment to PR...")
            post_comment(str(pr_number), comment)
        else:
            print(f"❌ Could not find PR number in event payload.")
    elif github_event_name == 'push':
        print(f"📦 Detected push to branch. Posting comment to commit {github_sha}...")
        post_commit_comment(github_sha, comment)
    else:
        print(f"❌ Could not determine where to post. Event={github_event_name}")

if __name__ == "__main__":
    main()