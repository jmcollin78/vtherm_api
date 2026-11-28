# Release

Only the maintainers publish. Agents prepare and check; they never tag, push or publish.

## Version

- Single source: `src/vtherm_api/__init__.py::__version__` (a PEP 440 string). `pyproject.toml` declares `dynamic = ["version"]` and reads it through `[tool.setuptools.dynamic]`. No other file carries the version.
- A version already on PyPI can never be reused (immutable). Pre-releases use PEP 440 forms (`1.2.3b1`) and are flagged as pre-release on GitHub.
- Bump the minor for a new capability, the patch for a fix or a documentation-only change. Never remove or change a published contract member.
- `tests/test_package.py` fails until the installed metadata is refreshed: run `python -m pip install -e .` after the bump.

## Changelog

No changelog file. The GitHub release notes are generated from the merged pull requests since the previous release (`gh release create --generate-notes` in `.github/workflows/release.yml`); commits pushed straight to `main` do not appear. Write pull request titles as release-note lines. User-visible documentation changes go in `documentation/en/` and `README.md`, not in a history section.

## Build and publication

Procedure and one-time setup (trusted publisher, `pypi` environment with required reviewers, tag ruleset): `publish.md` (in French). Verified in `.github/workflows/release.yml`:

1. Trigger: a pushed tag matching `[0-9]+.[0-9]+.[0-9]+*` or `v[0-9]+.[0-9]+.[0-9]+*`; other tags do nothing.
2. Job `validate`: refuses a tag that already has a GitHub release, runs `python -m build` and `twine check`, parses the tag with `packaging.version.Version` and requires `dist/vtherm_api-<version>-*.whl` and `.tar.gz` to exist (so `1.2.3b1`, `1.2.3-beta.1` and `v1.2.3b1` are the same version). It uploads `dist/` as an artifact.
3. Job `pypi` (environment `pypi`, `id-token: write`): publishes with `pypa/gh-action-pypi-publish` (trusted publishing, no token). May wait for a reviewer.
4. Job `github-release`: creates the release titled `vtherm_api <version>` with generated notes, `--prerelease` when the version is a pre-release.
5. A failed `github-release` after a successful upload: re-run the failed job only; never push the tag again. A partial upload: check PyPI files before any manual action (`publish.md`).

The release workflow runs no test: the gate is the `Tests` workflow (`.github/workflows/tests.yml`: the `api` job runs this repository's suite, the `vtherm` job runs VT's suite against this checkout) green on `main`.

## Cross-repository order

1. This package: contract change merged with tests and docs, version bumped, tag pushed, release visible on PyPI.
2. Versatile Thermostat: implement the new core-side members or calls, then raise its minimum `vtherm_api` requirement (the `requirements` of its integration manifest and its development requirements file, kept identical). The requirement cannot be installed before step 1 is complete.
3. Plugins: use the capability and raise their own minimum requirement and, when needed, the minimum VT version.

A VT or plugin manifest pointing to a git URL of this package is a local test edit only and is never committed.

## Checklist before tagging

1. `python -m pytest` green locally and CI green on `main`.
2. `__version__` bumped once; metadata refreshed; `python -m build && python -m twine check dist/*` clean locally if packaging changed (remove `dist/` and `build/` afterwards; they are ignored by git).
3. `documentation/en/` and `README.md` describe the released surface; the example version in `documentation/en/getting-started.md` (`requirements`) still makes sense.
4. Backward compatibility tests unchanged or deliberately extended; core-implemented additions are flagged for VT.
5. `python3 .agents/scripts/check_memory.py` passes; no private context in versioned files.
