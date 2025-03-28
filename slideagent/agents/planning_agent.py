from pydantic import BaseModel

from agents import Agent

from slideagent.settings.constants import DEFAULT_OPENAI_MODEL

PROMPT = """
    You are a Principle Software Engineering, skilled at:
        1. understanding the technical details of a GitHub repository and how they
           contribute to the product's success.
        2. identifying high-ticket contributions to a repo that must be communicated to 
           non-technical stakeholders.
    You use these skills to develop a research plan to brief executives on the
    most recent developments of a repository.
"""


class RepositorySearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""
    query: str
    """The search term to feed into a web (or file) search."""


class RepositorySearchPlan(BaseModel):
    searches: list[RepositorySearchItem]
    """A list of searches to perform."""


planner_agent = Agent(
    name="RepositoryPlannerAgent",
    instructions=PROMPT,
    model=DEFAULT_OPENAI_MODEL,
    output_type=RepositorySearchPlan,
)