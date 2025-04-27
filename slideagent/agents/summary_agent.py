from pydantic import BaseModel
from typing import List

from pydantic_ai import Agent
import asyncio
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

class PRSummary(BaseModel):
    high_level_summary: List[str]
    potential_breaking_changes: List[str]
    recommended_code_improvements: List[str]
    
system_prompt = """
You are an AI assistant tasked with analyzing GitHub Pull Request diffs, specifically for GitHub Actions workflows. Your goal is to produce a structured summary with the following sections:

1. High-Level Summary: Briefly describe the main changes introduced in the PR.
2. Potential Breaking Changes: Identify any modifications that might disrupt existing workflows or functionalities.
3. Recommended Code Improvements: Suggest enhancements or best practices to improve the code quality or security.

Ensure that your output strictly adheres to the following JSON schema:

{
  "high_level_summary": ["..."],
  "potential_breaking_changes": ["..."],
  "recommended_code_improvements": ["..."]
}
"""

# Initialize the agent with the specified model, output schema, and system prompt
agent = Agent(
    model="openai:gpt-4o",  # Replace with your preferred model
    result_type=PRSummary,
    system_prompt=system_prompt
)

# Define an asynchronous function to run the agent
async def analyze_pr_diff(pr_diff: str):
    result = await agent.run(pr_diff)
    return result.output

sample_diff = """
diff --git a/.github/workflows/deploy.yml b/.github/workflows/deploy.yml
index e69de29..b7f5f3c 100644
--- a/.github/workflows/deploy.yml
+++ b/.github/workflows/deploy.yml
@@ -0,0 +1,10 @@
+name: Deploy
+on:
+  push:
+    branches:
+      - main
+jobs:
+  deploy:
+    runs-on: ubuntu-latest
+    steps:
+      - uses: actions/checkout@v3
"""

# Run the agent with the sample diff
summary = asyncio.run(analyze_pr_diff(sample_diff))

# Output the structured summary
print(summary.model_dump_json(indent=2))
print("hello summit")
print("hello summit again")