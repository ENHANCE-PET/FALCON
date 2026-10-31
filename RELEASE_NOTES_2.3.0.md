# FALCON 2.3.0

Security and compatibility release. Requires Python 3.11 or newer.

- Invoke native tools with argument lists, preventing shell interpretation of
  image paths and supporting paths containing spaces. Registration arguments
  and processing defaults are preserved; subprocess failures now raise errors.
- Verify downloaded binary archives with pinned SHA-256 digests; validate and
  extract the expected bundle in private staging, ignoring Apple metadata.
  Upgrade legacy caches once, remove broad Windows permission grants, and
  preserve recoverable prior binaries if installation and rollback both fail.
- Require patched Python dependencies. Docker images build this release's source.

Validation: 18 regression tests; wheel/source build, CLI and dependency checks;
real macOS ARM64 native registration/resampling/downscale/correlation on synthetic
images, including paths containing spaces. Native argument vectors and the
deterministic downscale/correlation outputs match the previous implementation.
Registration varies even between repeated baseline runs, so bit-identical output
is not claimed. Full dynamic studies and Windows/Linux native execution were not
validated locally. No additional clinical validation is claimed.

Upgrade in a Python 3.11+ environment with `python -m pip install -U falconz`.
Existing binary caches are replaced once by verified copies, requiring network
access on the first run. See `SECURITY_AUDIT.md` for scope and remaining limits.
