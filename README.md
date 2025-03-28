# SlideAgent

SlideAgent is a Python-based project that leverages OpenAI's capabilities for intelligent slide-related operations. This project is currently in development (version 0.1.0).

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended for faster dependency resolution)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/walkerhughes/slideagent.git
cd slideagent
```

2. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create and activate a virtual environment with `uv`:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

4. Install dependencies and the package in editable mode:
```bash
uv pip install --editable .
```

## 📦 Dependencies

The project relies on the following main dependencies:
- `openai` (>=1.69.0) - OpenAI's Python client library
- `openai-agents` (>=0.0.7) - OpenAI's agent framework
- `pydantic` (>=2.11.0) - Data validation using Python type annotations

## 🏗️ Project Structure

```
slideagent/
├── .venv/              # Virtual environment directory
├── hello.py           # Initial example script
├── pyproject.toml     # Project configuration and dependencies
├── README.md          # This file
└── uv.lock            # Dependency lock file
```

## 🛠️ Development

The project uses Python 3.11+ and follows modern Python development practices. To start developing:

1. Activate your virtual environment
2. Make your changes
3. Run the example script:
```bash
python hello.py
```
