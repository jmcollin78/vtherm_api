from src import vtherm_api


def test_package_version() -> None:
    assert vtherm_api.__version__ == "0.1.0"
