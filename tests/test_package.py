from src import vtherm_api


def test_package_version() -> None:
    assert vtherm_api.__version__ == "0.2.0"


def test_package_exports_algorithm_plugin_api() -> None:
    assert vtherm_api.VThermAPI is not None
    assert vtherm_api.PluginClimate is not None
    assert vtherm_api.InterfaceThermostat is not None
    assert vtherm_api.InterfaceThermostatRuntime is not None
    assert vtherm_api.InterfaceCycleScheduler is not None
    assert vtherm_api.InterfacePropAlgorithmHandler is not None
    assert vtherm_api.InterfacePropAlgorithmFactory is not None
