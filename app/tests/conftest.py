# app/tests/conftest.py
import sys
from pathlib import Path

# This file makes sure your tests can import your app modules like:
#   import main
#   from orchestrator.scheduler import Scheduler
#   from api import settings
#
# It adjusts sys.path so that the app folder is on the import path.

# .../4155Capstone/app/tests/conftest.py
THIS_FILE = Path(__file__).resolve()

# .../4155Capstone/app
APP_DIR = THIS_FILE.parents[1]

# .../4155Capstone
PROJECT_ROOT = APP_DIR.parent

for path in (APP_DIR, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
