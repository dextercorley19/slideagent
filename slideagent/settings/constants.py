import os
from openai import OpenAI

# get the current working directory
PARENT_DIR = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# path to data relative to the parent directory
DATA_PATH = os.path.join(PARENT_DIR, "data")

# API clients
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LLM model names
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"