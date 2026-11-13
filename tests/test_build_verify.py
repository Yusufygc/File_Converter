"""
`build_verify.py` testleri: Inno AppId okuma ve deneme kurulumunun gerçek kaydı/kısayolu
bozmaması. Kayıt defterine yazmaz (hiç var olmayan bir GUID ile çalışır).
"""

from __future__ import annotations

from pathlib import Path
import uuid

import build_verify

ROOT = Path(__file__).resolve().parents[1]


def test_read_app_id_from_real_script() -> None:
    assert build_verify.read_app_id(ROOT / "packaging" / "FileConvert.iss") == "{8E478C22-671A-4D7A-A144-C9271DB89F42}"


def test_shortcuts_are_restored_after_trial_install(tmp_path: Path) -> None:
    fake_app_id = "{" + str(uuid.uuid4()).upper() + "}"  # gerçek kayıt yok -> geri yazılacak değer de yok
    start_menu = tmp_path / "Start Menu" / "FileConvert"
    start_menu.mkdir(parents=True)
    (start_menu / "FileConvert.lnk").write_bytes(b"gercek-kisayol")

    saved = build_verify.save_registration(fake_app_id, start_menu)
    assert saved.registry_values is None

    # Deneme kurulumu kısayolu ezdi/sildi
    (start_menu / "FileConvert.lnk").write_bytes(b"deneme-kisayolu")
    build_verify.restore_registration(fake_app_id, saved, start_menu)
    assert (start_menu / "FileConvert.lnk").read_bytes() == b"gercek-kisayol"


def test_trial_shortcuts_removed_when_no_real_install(tmp_path: Path) -> None:
    fake_app_id = "{" + str(uuid.uuid4()).upper() + "}"
    start_menu = tmp_path / "Start Menu" / "FileConvert"
    saved = build_verify.save_registration(fake_app_id, start_menu)  # gerçek kurulum yok

    start_menu.mkdir(parents=True)
    (start_menu / "FileConvert.lnk").write_bytes(b"deneme")
    build_verify.restore_registration(fake_app_id, saved, start_menu)
    assert not start_menu.exists()


def test_fatal_log_lines_detects_uncaught_errors(tmp_path: Path) -> None:
    log = tmp_path / "fileconvert.log"
    assert build_verify.fatal_log_lines(log) == []  # günlük yoksa hata da yok
    log.write_text(
        "2026-11-13 17:30:42,713 INFO fileconvert: FileConvert 1.1.0 başlatılıyor\n"
        "2026-11-13 17:30:44,398 CRITICAL fileconvert: Yakalanmamış hata\n",
        encoding="utf-8",
    )
    assert len(build_verify.fatal_log_lines(log)) == 1


def test_launch_check_treats_missing_exe_as_failure(tmp_path: Path) -> None:
    result = build_verify.launch_check(tmp_path / "yok.exe", seconds=1.0)
    assert result.ok is False and "Başlatılamadı" in result.detail
