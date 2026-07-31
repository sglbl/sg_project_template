"""CLI entry point for sg_project_template.

Run with either:
    python -m src.main ...        # preferred
    python src/main.py ...        # also works
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.presentation.cli import app 

if __name__ == "__main__":
    app(prog_name="./run")
