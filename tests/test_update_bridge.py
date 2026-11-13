"""
`UpdateBridge` durum makinesi testleri (ağ yok: servis işlevleri monkeypatch ile sahte).
Arka plan iş parçacığı yerine `_start` doğrudan çağrılır (senkron), böylece test deterministik.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def bridge(monkeypatch):
    from PySide6.QtWidgets import QApplication
    import sys

    if QApplication.instance() is None:
        QApplication(sys.argv)

    from ui_qml.bridge import update_bridge as ub

    def run_sync(self, job, on_ok, on_fail, on_progress=None):
        try:
            on_ok(job(on_progress or (lambda d, t: None)))
        except Exception as exc:  # noqa: BLE001
            on_fail(exc)

    monkeypatch.setattr(ub.UpdateBridge, "_start", run_sync)
    return ub, ub.UpdateBridge()


def _info(ub):
    return ub.UpdateInfo(
        version="9.9.9", tag="v9.9.9", asset_name="FileConvert-Setup-9.9.9.exe",
        download_url="https://github.com/Yusufygc/File_Converter/releases/download/v9.9.9/FileConvert-Setup-9.9.9.exe",
        size=10, sha256="0" * 64, sha256_url=None, notes="", html_url="",
    )


def test_startup_check_is_silent_when_disabled(bridge, monkeypatch) -> None:
    ub, b = bridge
    monkeypatch.setattr(ub.update_service, "update_check_allowed", lambda: False)
    monkeypatch.setattr(ub.update_service, "check_for_new_version", lambda **_: pytest.fail("ağa çıkılmamalı"))
    b.startupCheck()
    assert b.state == ub.STATE_IDLE and not b.dialogOpen


def test_manual_check_reports_up_to_date_and_errors_without_technical_text(bridge, monkeypatch) -> None:
    ub, b = bridge
    monkeypatch.setattr(ub.update_service, "check_for_new_version", lambda **_: None)
    b.checkNow()
    assert b.state == ub.STATE_UP_TO_DATE and b.dialogOpen

    def boom(**_):
        raise RuntimeError("Traceback: socket internals")

    monkeypatch.setattr(ub.update_service, "check_for_new_version", boom)
    b.closeDialog()
    b.checkNow()
    assert b.state == ub.STATE_ERROR
    assert "socket" not in b.message and "Traceback" not in b.message


def test_available_update_downloads_and_requests_quit(bridge, monkeypatch, tmp_path: Path) -> None:
    ub, b = bridge
    info = _info(ub)
    installer = tmp_path / info.asset_name
    monkeypatch.setattr(ub.update_service, "check_for_new_version", lambda **_: info)
    monkeypatch.setattr(ub.update_service, "download_installer", lambda i, progress=None: installer)
    launched: list[Path] = []
    monkeypatch.setattr(ub.update_service, "launch_installer", lambda p, log_dir=None: launched.append(p))

    b.checkNow()
    assert b.state == ub.STATE_AVAILABLE and b.newVersion == "9.9.9"
    b.startUpdate()
    assert launched == [installer]
    assert b.state == ub.STATE_INSTALLING


def test_blocked_installer_waits_and_retries(bridge, monkeypatch, tmp_path: Path) -> None:
    ub, b = bridge
    info = _info(ub)
    monkeypatch.setattr(ub.update_service, "check_for_new_version", lambda **_: info)
    monkeypatch.setattr(ub.update_service, "download_installer", lambda i, progress=None: tmp_path / info.asset_name)

    def blocked(p, log_dir=None):
        raise ub.InstallerBlockedError("engel")

    monkeypatch.setattr(ub.update_service, "launch_installer", blocked)
    monkeypatch.setattr(ub.UpdateBridge, "revealInstaller", lambda self: None)
    b.checkNow()
    b.startUpdate()
    assert b.state == ub.STATE_WAITING
    b.stopWaiting()
    assert b.state == ub.STATE_BLOCKED
