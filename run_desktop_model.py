import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "backend"))

from desktop_app import main

if __name__ == "__main__":
    main()
