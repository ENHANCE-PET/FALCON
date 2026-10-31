# Security review — 2026-10-31

Reviewed the current runtime source, dependency manifests, binary downloads,
and publishing workflows. Validation uses synthetic images and the published
macOS ARM64 native archive; no patient data was downloaded or committed.

## Repairs

- Replaced interpolated shell commands with argument lists for registration,
  resampling, downscaling, correlation, and format conversion. Synthetic filenames
  containing shell substitutions executed a harmless marker command before the fix;
  they now reach the executable unchanged. Failed subprocesses are reported.
- Removed the Windows `Everyone:(F)` grant on downloaded executables.
- Pinned all four native binary archive SHA-256 digests from GitHub release asset
  metadata. Downloads check HTTP status, have connect/read timeouts, and use
  private temporary storage. ZIP members must belong to the expected bundle and
  be regular files/directories, with no traversal or symbolic links. Existing
  installation directory links are rejected.
- Replace legacy binary caches once with verified fresh files, removing the old
  per-file Windows ACL grants. A digest marker permits subsequent cache reuse;
  failed verification preserves the previous installation.
- Ignore the `__MACOSX` metadata present in published archives without extracting
  it. Preserve the previous bundle in a separate recovery directory if both
  installation and rollback fail, and report that directory to the caller.
- Raised Pillow to `>=13.0.0`, Requests to `>=2.33.0`, and pydicom to `>=3.0.2`.
  Pillow requires Python 3.11, so package metadata, CI, Docker, and documentation
  use that minimum. `requirements.txt` now installs the same dependency policy
  as the package instead of stale conflicting pins.
- Added minimum fixed versions for the shared transitive packages certifi,
  fsspec, msgpack, tornado, and urllib3, so upgrades cannot retain versions affected
  by the advisories observed in LION's lockfile during this review.
- Docker builds the checked-out source rather than fetching an older PyPI release.
  Its context excludes incidental files. Publishing actions are pinned to verified
  commit SHAs and the Docker workflow has read-only repository permissions.

## Validation

- Full available test suite: **18 passed**, Python 3.13/macOS. Regressions were
  observed failing before repair. Tests use synthetic ZIPs, real filesystem
  operations, and a harmless executable that records its arguments.
- Package installation, `pip check`, `falconz --help`, bytecode compilation,
  wheel/source builds, and distribution metadata checks pass for 2.3.0.
- The actual published macOS ARM64 archive passes SHA-256 verification and the
  hardened installer. Its native `greedy` and `c3d` tools successfully process
  synthetic 32-cubed images through rigid, affine and deformable registration,
  resampling, downscaling and voxelwise correlation, including paths with spaces.
  Normalized native argument vectors match the previous implementation exactly;
  downscale/correlation arrays match exactly. Registration produces finite,
  correctly sized images and improves mean squared error from the shifted input.
  Registration itself varies between repeated baseline runs, so this check does
  not establish bit-identical registration outputs.
- Complete dependency resolution for the lowest supported Python 3.11 succeeds.
  `pip-audit` checked **72 resolved dependencies**, none skipped, and reported
  **no known vulnerabilities**. This is a dated database result, not a guarantee
  about all possible dependency combinations or undisclosed flaws.
- Independent code review and repeat regression run found no remaining blocker.

## Limits

Full dynamic motion-correction studies and Windows/Linux native execution were
not exercised on this Mac. Windows ACL inheritance was not exercised locally.
Cached files are trusted after installation; users with cache write access can
modify both binaries and their marker. Published digests establish byte identity
with the observed release, not independent provenance. Downloads/extraction have
no total size quota, and concurrent installations are not serialized.

## Sources

- [FALCON binary release metadata](https://api.github.com/repos/ENHANCE-PET/FALCON/releases/tags/falconz-v-2.2.2)
- [Pillow memory safety fixes](https://github.com/advisories/GHSA-5x8w-8jj5-q52h)
- [Requests temporary-file vulnerability](https://github.com/advisories/GHSA-gc5v-m9x4-r6x2)
- [pydicom FileSet traversal](https://github.com/advisories/GHSA-v856-2rf8-9f28)
