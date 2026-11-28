# Project

## What it is

`vtherm_api` is a pure-Python package published on PyPI. It defines the contracts between Versatile Thermostat (VT, the core integration) and its plugins: runtime-checkable protocols, immutable payload dataclasses, two registries, an event relay, an inhibition facade and logging helpers. It contains no thermostat logic: VT implements the core side of each contract, plugins implement the other side and import only this package.

## Related repositories

| Repository | Relation |
| --- | --- |
| `versatile_thermostat` | The core. Implements `InterfaceThermostatRuntime`, `InterfaceCycleScheduler` and their optional extensions, calls the optional hooks of feature managers, uses the registries and the logging helpers. Its integration manifest and its development requirements file carry the minimum `vtherm_api` version it needs. |
| `vtherm_smartpi` | Algorithm plugin (named by the documentation): registers an `InterfacePropAlgorithmFactory`. Other plugins follow the same registration pattern. |
| `vtherm_climate_replication` | Uses `PluginClimate` as a link and service-forwarding helper (named by the documentation). |
| the VT dashboard | Reads the UI plugin registry (`VThermAPI.get_ui_plugins`) and interprets its entries. |

## Versions and dependencies

- Version: the string `src/vtherm_api/__init__.py::__version__`; `pyproject.toml` reads it dynamically (`workflows/release.md`).
- `requires-python = ">=3.13"` in `pyproject.toml`; CI, the devcontainer and the documentation use 3.14.
- `dependencies = []`: the package declares no runtime dependency. It imports `homeassistant` (and `aiohttp` in `src/vtherm_api/log_collector.py`), which the host Home Assistant provides. `requirements-dev.txt` pins the Home Assistant version used to test.
- Dev tools: `pytest`, `pytest-asyncio` (strict mode: async tests carry `@pytest.mark.asyncio`), `build`, `twine`.

## Conventions

- Source layout `src/vtherm_api/`; public names are exported from `src/vtherm_api/__init__.py` (`__all__`). `EventType`, `DOMAIN`, the other constants and `build_ui_plugin` are reachable only through their module.
- English docstrings and comments in new code. Some older docstrings in `src/vtherm_api/interfaces.py` are in French: leave them unless the member changes.
- Formatting: line length 180 (`pyproject.toml` black section and `.pylintrc`). Pylint disables are written inline with a reason.
- Dataclasses of contracts are `@dataclass(frozen=True, slots=True)`; contracts are `@runtime_checkable` `Protocol` classes.
- Documentation: `documentation/en/` (api-reference, architecture, events, getting-started, overview, testing, guides) and `README.md`; `documentation/tech-docs/` holds design notes written with the maintainers' `tech-doc` Copilot profile. The packaging guide `publish.md` is in French.
- Maintainer rule: the package is upstream-bound; no personal data, plan or review references, URLs of private systems or machine paths in any versioned file.
