# Python 3.14 Packaging Compatibility Design

## Context

FalconZ 2.2.2 declares support for every Python version from 3.10 onward while
pinning NumPy to the 1.25 release line. A fresh Conda environment currently
selects Python 3.14, for which NumPy 1.25 has no wheel. Pip consequently tries
to build NumPy 1.25.2 from source and fails while importing its legacy
`setuptools.build_meta` backend.

Reproducing the installation on Python 3.14.2 outside Conda produced the same
traceback, proving that Conda is the trigger for selecting Python 3.14 rather
than the failing component. A dependency-relaxed experiment found two more
runtime incompatibilities: nibabel 3.2.2 uses a NumPy API removed in NumPy 2,
and pyfiglet 0.8.post1 imports the removed `pkg_resources` module.

## Goals

- Make a clean `pip install falconz` work on CPython 3.10 through 3.14.
- Preserve the existing Python 3.10 and 3.11 installation path.
- Test installation on both operating systems reported in issue #63.
- Prevent the release workflow from uploading an artifact that cannot be
  installed and imported.
- Give Conda users an explicit, reproducible environment command.

## Non-goals

- Change motion-correction behavior or image-processing algorithms.
- Refactor FalconZ's runtime modules.
- Replace the existing PyPI API-token authentication in this patch.
- Guarantee support for future, unreleased Python versions.

## Package metadata

Release the fix as FalconZ 2.2.3. Keep `python_requires` at `>=3.10`, align the
classifiers with Python 3.10 through 3.14, and update the three incompatible
dependency constraints:

- `numpy>=1.25.2`
- `nibabel>=5.4.2`
- `pyfiglet>=1.0.4`

Minimum bounds preserve pip's ability to choose the newest release compatible
with each supported Python version. The application does not import NumPy
directly, and its nibabel usage is limited to stable image loading, saving,
construction, and concatenation APIs. Keep `requirements.txt` aligned with the
package metadata for developers installing from the repository.

## Installation documentation

State that FalconZ supports Python 3.10 through 3.14. Add Conda examples that
select Python explicitly and invoke pip through the active interpreter:

```bash
conda create -n falconz python=3.14 pip
conda activate falconz
python -m pip install falconz
```

Using `python -m pip` makes it visible which interpreter receives the package.

## Continuous integration

Add a package-install workflow for pull requests and pushes to `main`. Test the
supported Python endpoints, 3.10 and 3.14, on macOS and Windows. Each job will:

1. Install the repository as a package.
2. Run `python -m pip check`.
3. Run `falconz --help` to exercise FalconZ's real import graph.

The existing PyPI workflow directly publishes on the `release.published`
event using `PYPI_API_TOKEN`. Retain that authentication and trigger, but add a
pre-publication smoke test: build the wheel and source distribution, install
the generated wheel with dependencies on the Ubuntu release runner, run
`pip check`, and run `falconz --help`. The publish action must upload those same
validated files from `dist/`.

## Regression strategy

The original failure signal is a clean Python 3.14 installation of FalconZ
2.2.2 ending in `BackendUnavailable: Cannot import 'setuptools.build_meta'`.
Before changing metadata, codify the clean-install and CLI-smoke sequence in CI
and run its equivalent against the existing package to retain the red signal.
After the metadata change, run the same sequence against a locally built wheel.

Acceptance requires:

- Clean endpoint installations complete without source-building NumPy 1.25.
- `pip check` reports no broken requirements.
- FalconZ imports and `falconz --help` exits successfully.
- The built wheel reports version 2.2.3, Python `>=3.10`, and the new bounds.
- The release workflow cannot reach its PyPI upload step if artifact validation
  fails.

## Release note

The issue response should explain that an unpinned Conda environment selected
Python 3.14, expose the Python 3.11 workaround for FalconZ 2.2.2, and state that
FalconZ 2.2.3 adds Python 3.14-compatible dependency metadata.
