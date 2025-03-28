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
```

4. Install dependencies and the package in editable mode:
```bash
uv pip install -e .
```

1. Use paths relative to parent directory
```python
from slideagent.settings.constants import OPENAI_CLIENT
```