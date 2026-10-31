# FALCON 2.3.1

Follow-up to the 2.3.0 security release. Requires Python 3.11 or newer.

Replace the obsolete dicom2nifti 2.4-only dependency constraint with >=2.6.2,
compatible with patched pydicom and LION 1.1.0. The previous constraints prevented
FALCON 2.3.0 and LION 1.1.0 from being installed in one environment. Combined
dependency resolution failed before this change and succeeds afterward.
All 18 FALCON regression tests pass. Processing code and native arguments are
unchanged from 2.3.0.

This includes the 2.3.0 shell-injection, verified-download, cache-recovery and
dependency fixes. Use `python -m pip install -U falconz` in Python 3.11+.
Existing binary caches refresh once and need writable storage/network access.
See RELEASE_NOTES_2.3.0.md and SECURITY_AUDIT.md for validation scope and limits.
