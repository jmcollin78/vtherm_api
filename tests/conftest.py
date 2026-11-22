"""Pytest configuration for repository-local imports."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# The integration job runs this test from VTherm's tests directory for its fixtures.
collect_ignore = ["test_api_temperature_timestamps.py"]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
