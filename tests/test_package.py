from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import vtherm_api


def test_package_version() -> None:
    assert vtherm_api.__version__ == "0.1.0"
