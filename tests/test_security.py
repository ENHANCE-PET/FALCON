"""Security regressions using synthetic paths and a harmless CLI stand-in."""

import io
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import zipfile

import pytest
import requests

from falconz import download, file_utilities, image_conversion, image_processing


@pytest.fixture
def recorder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    log = tmp_path / "arguments.jsonl"
    executable = tmp_path / "recorder"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, sys\n"
        f"with open({str(log)!r}, 'a') as stream:\n"
        "    stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
    )
    executable.chmod(0o700)
    for module in (image_processing, image_conversion):
        monkeypatch.setattr(module, "C3D_PATH", str(executable))
    monkeypatch.setattr(image_processing, "GREEDY_PATH", str(executable))
    return log


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable fixture")
@pytest.mark.parametrize("operation", ["rigid", "affine", "deformable", "resample", "downscale", "ncc", "convert"])
def test_image_paths_are_literal_arguments(tmp_path, recorder, operation):
    image = str(tmp_path / "scan$(touch PWNED).nii")
    fixed = str(tmp_path / "fixed image.nii")
    output = str(tmp_path / "output image.nii")
    registration = image_processing.ImageRegistration(fixed, "100x25x10", fixed_mask=fixed)
    registration.set_moving_image(image)
    if operation in ("rigid", "affine", "deformable"):
        getattr(registration, operation)()
    elif operation == "resample":
        registration.resample(output, "deformable", image, output)
    elif operation == "downscale":
        image_processing.downscale_image((str(tmp_path), 2), image)
    elif operation == "ncc":
        image_processing.calc_voxelwise_ncc_images(fixed, image, str(tmp_path))
    else:
        converter = image_conversion.NiftiConverter.__new__(image_conversion.NiftiConverter)
        converter.output_directory = str(tmp_path)
        converter._convert_to_nifti_format(image).compute(scheduler="synchronous")
    assert not (tmp_path / "PWNED").exists()
    calls = [json.loads(line) for line in recorder.read_text().splitlines()]
    assert image in calls[0]
    if operation in ("rigid", "affine", "deformable"):
        assert calls[0][calls[0].index("-m") + 1:] == ["NCC", "2x2x2"]
        assert calls[0][calls[0].index("-gm") + 1] == fixed


def test_windows_permissions_preserve_existing_acl(monkeypatch):
    def unexpected_acl_change(*args, **kwargs):
        pytest.fail("Downloaded executables must not grant access to other users")

    monkeypatch.setattr(file_utilities.subprocess, "check_call", unexpected_acl_change)
    file_utilities.set_permissions("greedy.exe", "windows")


def mock_archive(monkeypatch, entries, status_error=False):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as stream:
        for name, data in entries:
            stream.writestr(name, data)

    class Response:
        headers = {"Content-Length": str(len(archive.getvalue()))}

        def raise_for_status(self):
            if status_error:
                raise requests.HTTPError("404 Not Found")

        def iter_content(self, chunk_size):
            yield archive.getvalue()

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    monkeypatch.setattr(download.requests, "get", lambda *args, **kwargs: Response())
    return hashlib.sha256(archive.getvalue()).hexdigest()


def install(tmp_path):
    return download.download("binary", str(tmp_path), {
        "binary": {"url": "https://example.test/binary.zip", "filename": "binary.zip", "directory": "bundle"}
    })


def test_download_rejects_unexpected_archive_root(tmp_path, monkeypatch):
    mock_archive(monkeypatch, [("bundle/greedy", b"binary"), ("unrelated", b"overwrite")])
    with pytest.raises(ValueError):
        install(tmp_path)
    assert not (tmp_path / "unrelated").exists()
    assert not (tmp_path / "bundle").exists()


def test_download_does_not_follow_existing_directory_link(tmp_path, monkeypatch):
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "bundle").symlink_to(outside, target_is_directory=True)
    mock_archive(monkeypatch, [("bundle/greedy", b"binary")])
    with pytest.raises(ValueError):
        install(tmp_path)
    assert list(outside.iterdir()) == []


def test_download_rejects_archive_symlinks(tmp_path, monkeypatch):
    link = zipfile.ZipInfo("bundle/greedy")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    mock_archive(monkeypatch, [(link, b"../../outside")])
    with pytest.raises(ValueError):
        install(tmp_path)
    assert not (tmp_path / "bundle").exists()


def test_download_checks_http_errors_before_installing(tmp_path, monkeypatch):
    mock_archive(monkeypatch, [("bundle/greedy", b"binary")], status_error=True)
    with pytest.raises(requests.HTTPError):
        install(tmp_path)
    assert not (tmp_path / "bundle").exists()


def test_download_rejects_incorrect_published_digest(tmp_path, monkeypatch):
    mock_archive(monkeypatch, [("bundle/greedy", b"binary")])
    with pytest.raises(ValueError, match="SHA-256"):
        download.download("binary", str(tmp_path), {"binary": {
            "url": "https://example.test/binary.zip", "filename": "binary.zip",
            "directory": "bundle", "sha256": "0" * 64,
        }})
    assert not (tmp_path / "bundle").exists()


def test_download_refreshes_legacy_cache_before_reusing_it(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "greedy").write_bytes(b"legacy unverified executable")
    digest = mock_archive(monkeypatch, [("bundle/greedy", b"verified binary")])
    items = {"binary": {
        "url": "https://example.test/binary.zip", "filename": "binary.zip",
        "directory": "bundle", "sha256": digest,
    }}
    download.download("binary", str(tmp_path), items)
    assert (bundle / "greedy").read_bytes() == b"verified binary"

    def unexpected_download(*args, **kwargs):
        pytest.fail("A verified cache should be reused")

    monkeypatch.setattr(download.requests, "get", unexpected_download)
    download.download("binary", str(tmp_path), items)


def test_failed_refresh_preserves_existing_cache(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "greedy").write_bytes(b"existing binary")
    mock_archive(monkeypatch, [("bundle/greedy", b"tampered binary")])
    with pytest.raises(ValueError, match="SHA-256"):
        download.download("binary", str(tmp_path), {"binary": {
            "url": "https://example.test/binary.zip", "filename": "binary.zip",
            "directory": "bundle", "sha256": "0" * 64,
        }})
    assert (bundle / "greedy").read_bytes() == b"existing binary"


def test_failed_install_and_rollback_keep_recoverable_backup(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "greedy").write_bytes(b"existing binary")
    digest = mock_archive(monkeypatch, [("bundle/greedy", b"replacement binary")])
    rename = Path.rename

    def fail_publication_and_restore(path, target):
        if path.parent.name == "extracted" or path.name == "previous":
            raise OSError("simulated installation/rollback failure")
        return rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_publication_and_restore)
    with pytest.raises((OSError, RuntimeError)):
        download.download("binary", str(tmp_path), {"binary": {
            "url": "https://example.test/binary.zip", "filename": "binary.zip",
            "directory": "bundle", "sha256": digest,
        }})
    backups = list(tmp_path.glob(".falcon-backup-*/previous/greedy"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"existing binary"


def test_download_ignores_stale_archive_and_installs_expected_tree(tmp_path, monkeypatch):
    (tmp_path / "binary.zip").write_bytes(b"stale incomplete download")
    mock_archive(monkeypatch, [("bundle/greedy", b"binary")])
    install(tmp_path)
    assert (tmp_path / "bundle" / "greedy").read_bytes() == b"binary"


def test_download_ignores_macos_metadata_without_extracting_it(tmp_path, monkeypatch):
    mock_archive(monkeypatch, [
        ("bundle/greedy", b"binary"),
        ("__MACOSX/._bundle", b"Finder metadata"),
        ("__MACOSX/bundle/._greedy", b"Finder metadata"),
    ])
    install(tmp_path)
    assert (tmp_path / "bundle" / "greedy").read_bytes() == b"binary"
    assert not (tmp_path / "__MACOSX").exists()
