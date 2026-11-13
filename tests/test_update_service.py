"""
`core/update_service.py` testleri. Ağ yok: tüm istekler sahte `opener` ile.
Güvenlik kuralları (host listesi, sıkı ad, boyut, zorunlu SHA-256) burada sabitlenir.
"""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
import urllib.error

import pytest

from core import update_service as us

REPO = "Yusufygc/File_Converter"
PAYLOAD = b"kurulum-dosyasi-icerigi" * 100


def _release(version: str = "9.9.9", *, digest: bool = True, sha_asset: bool = False, size: int | None = None,
             url: str | None = None, prerelease: bool = False) -> dict:
    name = f"FileConvert-Setup-{version}.exe"
    installer = {
        "name": name,
        "size": len(PAYLOAD) if size is None else size,
        "browser_download_url": url or f"https://github.com/{REPO}/releases/download/v{version}/{name}",
    }
    if digest:
        installer["digest"] = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()
    assets = [installer]
    if sha_asset:
        assets.append({
            "name": name + ".sha256",
            "browser_download_url": f"https://github.com/{REPO}/releases/download/v{version}/{name}.sha256",
        })
    return {"tag_name": f"v{version}", "assets": assets, "body": "Notlar", "prerelease": prerelease,
            "html_url": f"https://github.com/{REPO}/releases/tag/v{version}"}


def _opener(responses: dict[str, bytes | Exception]):
    @contextmanager
    def _open(request):
        value = responses[request.full_url]
        if isinstance(value, Exception):
            raise value
        yield io.BytesIO(value)

    return _open


# ---------------------------------------------------------------- sürüm


def test_version_comparison_is_numeric_and_ignores_prerelease() -> None:
    assert us.is_newer("1.10.0", "1.9.0")
    assert not us.is_newer("1.1.0", "1.1.0")
    assert not us.is_newer("v2.0.0-rc1", "1.0.0")
    assert us.parse_version("v1.2.3") == (1, 2, 3)


def test_release_to_update_filters_old_prerelease_and_missing_asset() -> None:
    assert us.release_to_update(_release("1.0.0"), "1.1.0", REPO) is None
    assert us.release_to_update(_release("9.9.9", prerelease=True), "1.1.0", REPO) is None
    release = _release("9.9.9")
    release["assets"][0]["name"] = "Baska-Ad.exe"
    assert us.release_to_update(release, "1.1.0", REPO) is None
    info = us.release_to_update(_release("9.9.9"), "1.1.0", REPO)
    assert info is not None and info.version == "9.9.9" and info.sha256


def test_download_url_must_be_this_repo_on_github() -> None:
    with pytest.raises(us.UpdateError):
        us.release_to_update(_release(url="https://evil.example.com/FileConvert-Setup-9.9.9.exe"), "1.1.0", REPO)
    with pytest.raises(us.UpdateError):
        us.validate_download_url("https://github.com/baska/depo/releases/download/v1/x.exe", REPO)
    with pytest.raises(us.UpdateError):
        us.validate_download_url(f"http://github.com/{REPO}/releases/download/v1/x.exe", REPO)


def test_size_limits_are_enforced() -> None:
    with pytest.raises(us.UpdateError):
        us.release_to_update(_release(size=0), "1.1.0", REPO)
    with pytest.raises(us.UpdateError):
        us.release_to_update(_release(size=us.MAX_INSTALLER_BYTES + 1), "1.1.0", REPO)


def test_no_release_yet_is_not_an_error() -> None:
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    not_found = urllib.error.HTTPError(url, 404, "Not Found", None, None)
    assert us.fetch_latest_release(REPO, _opener({url: not_found})) == {}


def test_network_failure_message_has_no_technical_text() -> None:
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    with pytest.raises(us.UpdateError) as info:
        us.fetch_latest_release(REPO, _opener({url: urllib.error.URLError("getaddrinfo failed")}))
    assert "getaddrinfo" not in str(info.value)


# ---------------------------------------------------------------- indirme


def test_download_verifies_sha256_and_size(tmp_path: Path) -> None:
    info = us.release_to_update(_release(), "1.1.0", REPO)
    assert info is not None
    progress: list[tuple[int, int]] = []
    path = us.download_installer(info, tmp_path, lambda d, t: progress.append((d, t)),
                                 _opener({info.download_url: PAYLOAD}), REPO)
    assert path.read_bytes() == PAYLOAD and path.name == "FileConvert-Setup-9.9.9.exe"
    assert progress[-1] == (len(PAYLOAD), len(PAYLOAD))


def test_download_rejects_hash_mismatch_and_deletes_file(tmp_path: Path) -> None:
    info = us.release_to_update(_release(), "1.1.0", REPO)
    assert info is not None
    tampered = b"x" * len(PAYLOAD)
    with pytest.raises(us.UpdateError):
        us.download_installer(info, tmp_path, None, _opener({info.download_url: tampered}), REPO)
    assert list(tmp_path.iterdir()) == []


def test_download_falls_back_to_sha256_file_and_requires_a_hash(tmp_path: Path) -> None:
    info = us.release_to_update(_release(digest=False, sha_asset=True), "1.1.0", REPO)
    assert info is not None and info.sha256 is None and info.sha256_url
    sha_text = f"{hashlib.sha256(PAYLOAD).hexdigest()} *{info.asset_name}\n".encode()
    path = us.download_installer(info, tmp_path, None,
                                 _opener({info.sha256_url: sha_text, info.download_url: PAYLOAD}), REPO)
    assert path.is_file()

    no_hash = us.release_to_update(_release(digest=False, sha_asset=False), "1.1.0", REPO)
    assert no_hash is not None
    with pytest.raises(us.UpdateError):  # özet yoksa güncelleme reddedilir
        us.download_installer(no_hash, tmp_path / "b", None, _opener({no_hash.download_url: PAYLOAD}), REPO)


def test_download_rejects_oversized_stream(tmp_path: Path) -> None:
    info = us.release_to_update(_release(), "1.1.0", REPO)
    assert info is not None
    with pytest.raises(us.UpdateError):
        us.download_installer(info, tmp_path, None, _opener({info.download_url: PAYLOAD + b"fazla"}), REPO)


# ---------------------------------------------------------------- kurulum


def test_launch_installer_uses_fixed_silent_arguments(tmp_path: Path) -> None:
    installer = tmp_path / "FileConvert-Setup-9.9.9.exe"
    installer.write_bytes(b"x")
    calls: list[list[str]] = []
    us.launch_installer(installer, tmp_path, popen=lambda args, **_: calls.append(args))
    assert calls[0][1:4] == ["/SILENT", "/SUPPRESSMSGBOXES", "/CLOSEAPPLICATIONS"]
    assert calls[0][4].startswith("/LOG=")


def test_launch_installer_rejects_unexpected_name(tmp_path: Path) -> None:
    other = tmp_path / "virus.exe"
    other.write_bytes(b"x")
    with pytest.raises(us.UpdateError):
        us.launch_installer(other, tmp_path, popen=lambda *a, **k: None)


def test_blocked_installer_falls_back_to_shell_then_raises(tmp_path: Path) -> None:
    installer = tmp_path / "FileConvert-Setup-9.9.9.exe"
    installer.write_bytes(b"x")

    def blocked(*_a, **_k):
        error = OSError("blocked")
        error.winerror = 4551  # type: ignore[attr-defined]
        raise error

    us.launch_installer(installer, tmp_path, popen=blocked, shell_execute=lambda p, a: 42)  # Gezgin yolu açtı
    with pytest.raises(us.InstallerBlockedError):
        us.launch_installer(installer, tmp_path, popen=blocked, shell_execute=lambda p, a: 5)


# ---------------------------------------------------------------- tercihler


def test_preferences_roundtrip_and_env_switch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FILECONVERT_HOME", str(tmp_path))
    monkeypatch.delenv(us.NO_UPDATE_CHECK_ENV, raising=False)
    assert us.update_check_allowed()
    us.set_update_check_on_startup(False)
    us.skip_update_version("9.9.9")
    prefs = json.loads((tmp_path / "updates.json").read_text(encoding="utf-8"))
    assert prefs == {"check_on_startup": False, "skipped_version": "9.9.9"}
    assert not us.update_check_allowed()

    us.set_update_check_on_startup(True)
    monkeypatch.setenv(us.NO_UPDATE_CHECK_ENV, "1")
    assert not us.update_check_allowed()


def test_corrupt_preferences_fall_back_to_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FILECONVERT_HOME", str(tmp_path))
    (tmp_path / "updates.json").write_text("{bozuk", encoding="utf-8")
    assert us.load_preferences() == us.UpdatePreferences()



def test_install_mode_follows_running_installation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    local = tmp_path / "Local"
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    per_user = local / "Programs" / "FileConvert"
    per_user.mkdir(parents=True)
    all_users = tmp_path / "Program Files" / "FileConvert"
    all_users.mkdir(parents=True)

    assert us.install_mode_arguments(per_user) == ["/CURRENTUSER"]
    assert us.install_mode_arguments(all_users) == ["/ALLUSERS"]
    assert us.install_mode_arguments(None) == []  # kaynak koddan çalışırken mod zorlanmaz

    args = us.installer_arguments(tmp_path / "FileConvert-Setup-9.9.9.exe", tmp_path, per_user)
    assert "/CURRENTUSER" in args and args[-1].startswith("/LOG=")
