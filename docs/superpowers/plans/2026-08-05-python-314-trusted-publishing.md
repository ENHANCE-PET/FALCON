# Python 3.14 and Trusted Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release FalconZ 2.2.3 with installable Python 3.10–3.14 metadata and replace the long-lived PyPI token in the release workflow with PyPI Trusted Publishing.

**Architecture:** Package installation is treated as an integration boundary: CI installs FalconZ in clean endpoint interpreters and exercises the CLI import graph. The release workflow builds distributions once, validates the wheel, transfers those exact files to an isolated OIDC-authorized publish job, and uploads only after validation succeeds.

**Tech Stack:** setuptools, pip, Python build, GitHub Actions, PyPA publish action, PyPI OIDC Trusted Publishing.

## Global Constraints

- Support CPython 3.10 through 3.14.
- Use `numpy>=1.25.2`, `nibabel>=5.4.2`, and `pyfiglet>=1.0.4`.
- Do not alter motion-correction or image-processing behavior.
- Test clean installation on macOS and Windows at Python 3.10 and 3.14.
- Publish only distributions that passed `pip check` and `falconz --help`.
- Authorize PyPI only through `ENHANCE-PET/FALCON`, `python-publish.yml`, and the `pypi` GitHub environment.
- Leave `PYPI_API_TOKEN` stored but unused until the first successful OIDC release.

---

### Task 1: Add the packaging regression workflow

**Files:**
- Create: `.github/workflows/python-package.yml`

**Interfaces:**
- Consumes: FalconZ package metadata from `setup.py`.
- Produces: A clean-install signal for pull requests and pushes to `main`.

- [ ] **Step 1: Add the endpoint installation workflow**

Create `.github/workflows/python-package.yml` with this complete workflow:

```yaml
name: Test Python package

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  install:
    name: Python ${{ matrix.python-version }} on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [macos-latest, windows-latest]
        python-version: ['3.10', '3.14']

    steps:
      - name: Check out repository
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - name: Set up Python
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: ${{ matrix.python-version }}
      - name: Upgrade pip
        run: python -m pip install --upgrade pip
      - name: Install FalconZ
        run: python -m pip install .
      - name: Check dependencies
        run: python -m pip check
      - name: Smoke-test CLI
        run: falconz --help
```

- [ ] **Step 2: Verify the regression is red against 2.2.2 metadata**

Run the equivalent clean Python 3.14 command:

```bash
/private/tmp/falcon-python-install/cpython-3.14.2-macos-aarch64-none/bin/python3.14 -m venv /private/tmp/falcon-issue63-red
/private/tmp/falcon-issue63-red/bin/python -m pip install .
```

Expected: FAIL while pip prepares `numpy-1.25.2.tar.gz`, ending with
`BackendUnavailable: Cannot import 'setuptools.build_meta'`.

- [ ] **Step 3: Validate workflow syntax**

Run:

```bash
ruby -e "require 'yaml'; YAML.load_file('.github/workflows/python-package.yml', aliases: true)"
```

Expected: exit 0.

- [ ] **Step 4: Commit the regression workflow**

```bash
git add .github/workflows/python-package.yml
git commit -m "ci: test package installation endpoints"
```

### Task 2: Modernize package compatibility metadata

**Files:**
- Modify: `setup.py`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: the clean-install signal from Task 1.
- Produces: FalconZ 2.2.3 metadata resolvable on Python 3.10–3.14.

- [ ] **Step 1: Update release and dependency metadata**

Set the release version and bounds in `setup.py`:

```python
version='2.2.3'
python_requires='>=3.10'
```

Replace obsolete Python classifiers with explicit classifiers for 3.10, 3.11,
3.12, 3.13, and 3.14. Replace the three dependency constraints with:

```python
'nibabel>=5.4.2'
'numpy>=1.25.2'
'pyfiglet>=1.0.4'
```

- [ ] **Step 2: Align developer requirements**

In `requirements.txt`, use the same three lower bounds and retain the remaining
existing requirements.

- [ ] **Step 3: Build the distributions**

Run:

```bash
python3 -m build
```

Expected: exit 0 with one wheel and one source distribution in `dist/`.

- [ ] **Step 4: Verify wheel metadata independently**

Run a Python script using `zipfile` and `email.parser` to read the wheel's
`METADATA`. Assert these literal values:

```text
Version: 2.2.3
Requires-Python: >=3.10
Requires-Dist: numpy>=1.25.2
Requires-Dist: nibabel>=5.4.2
Requires-Dist: pyfiglet>=1.0.4
```

Expected: exit 0.

- [ ] **Step 5: Verify the Python 3.14 clean install turns green**

Install the newly built wheel into a fresh Python 3.14 environment, then run:

```bash
python -m pip check
falconz --help
```

Expected: both commands exit 0 and pip selects a Python 3.14 NumPy wheel.

- [ ] **Step 6: Commit package metadata**

```bash
git add setup.py requirements.txt
git commit -m "fix: support installation on Python 3.14"
```

### Task 3: Document supported and Conda installations

**Files:**
- Modify: `README.md`
- Modify: `docs/installation.rst`

**Interfaces:**
- Consumes: supported Python range and dependency behavior from Task 2.
- Produces: reproducible virtualenv and Conda instructions for users.

- [ ] **Step 1: Correct the supported Python range**

State that FalconZ supports Python 3.10 through 3.14. Remove the existing
documentation claim that Python 3.6 or newer is supported.

- [ ] **Step 2: Add explicit Conda instructions**

Add this command sequence to both installation guides:

```bash
conda create -n falconz python=3.14 pip
conda activate falconz
python -m pip install falconz
```

Use `python -m pip install falconz` in virtualenv instructions as well.

- [ ] **Step 3: Review rendered source structure**

Run:

```bash
git diff --check
```

Expected: exit 0 with no whitespace errors.

- [ ] **Step 4: Commit installation documentation**

```bash
git add README.md docs/installation.rst
git commit -m "docs: add supported Conda installation"
```

### Task 4: Gate releases and migrate the workflow to OIDC

**Files:**
- Modify: `.github/workflows/python-publish.yml`

**Interfaces:**
- Consumes: the buildable package from Task 2.
- Produces: validated `dist/` artifacts and an OIDC-only PyPI publication job.

- [ ] **Step 1: Split build verification from publication**

Replace `.github/workflows/python-publish.yml` with this complete workflow. The
`build-and-verify` job has no OIDC permission, and the `publish` job cannot run
unless artifact validation succeeds:

```yaml
name: Upload Python Package

on:
  release:
    types: [published]

permissions: {}

jobs:
  build-and-verify:
    name: Build and verify distributions
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Check out repository
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - name: Set up Python
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: '3.14'
      - name: Install build tooling
        run: python -m pip install --upgrade pip build
      - name: Build distributions
        run: python -m build
      - name: Install built wheel
        run: python -m pip install dist/*.whl
      - name: Check dependencies
        run: python -m pip check
      - name: Smoke-test CLI
        run: falconz --help
      - name: Store distributions
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: python-package-distributions
          path: dist/
          if-no-files-found: error

  publish:
    name: Publish distributions to PyPI
    needs: build-and-verify
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/falconz
    permissions:
      id-token: write
    steps:
      - name: Retrieve distributions
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
        with:
          name: python-package-distributions
          path: dist/
      - name: Publish distributions
        uses: pypa/gh-action-pypi-publish@dc37677b2e1c63e2034f94d8a5b11f265b73ba33 # v1.14.2
```

- [ ] **Step 2: Confirm the trust boundary**

Verify that only `publish` receives `id-token: write`, only `publish` references
the `pypi` environment, and the publish action receives no explicit inputs.

- [ ] **Step 3: Validate workflow syntax and source invariants**

Run the YAML parser against both workflows. Then run:

```bash
rg -n "PYPI_API_TOKEN|password:|user:" .github/workflows
```

Expected: no matches in `python-publish.yml`.

- [ ] **Step 4: Commit the secured release workflow**

```bash
git add .github/workflows/python-publish.yml
git commit -m "ci: publish to PyPI with trusted publishing"
```

### Task 5: Configure the external trust relationship

**Files:**
- No repository files.

**Interfaces:**
- Consumes: `.github/workflows/python-publish.yml` and its `pypi` environment.
- Produces: matching GitHub and PyPI OIDC configuration.

- [ ] **Step 1: Ensure the GitHub environment exists**

Read `repos/ENHANCE-PET/FALCON/environments/pypi`. If absent, create the exact
`pypi` environment without deployment branch restrictions. Do not alter or
delete repository secrets.

- [ ] **Step 2: Register PyPI's trusted publisher**

In FalconZ's PyPI project publishing settings, add a GitHub publisher with:

```text
Owner: ENHANCE-PET
Repository: FALCON
Workflow: python-publish.yml
Environment: pypi
```

If PyPI requires interactive login or 2FA, pause for the owner to authenticate,
then resume the same browser session.

- [ ] **Step 3: Verify the publisher record**

Confirm the PyPI settings page shows all four values exactly. Do not perform a
test upload, create a release, or delete `PYPI_API_TOKEN`.

### Task 6: Final verification

**Files:**
- Verify all changed files.

**Interfaces:**
- Consumes: all previous tasks.
- Produces: evidence for review and release preparation.

- [ ] **Step 1: Run fresh local artifact checks**

Rebuild from a clean `dist/`, install the wheel on Python 3.14, run `pip check`,
and run `falconz --help`.

- [ ] **Step 2: Run repository checks**

Run:

```bash
git diff --check
git status --short
```

Inspect every changed file and confirm no generated build products or Python
cache files are tracked.

- [ ] **Step 3: Report release instructions**

Report the exact commits, verification outputs, PyPI publisher configuration,
and the fact that publishing still occurs only when a GitHub Release is
published. Recommend deleting `PYPI_API_TOKEN` only after the first successful
OIDC publication.
