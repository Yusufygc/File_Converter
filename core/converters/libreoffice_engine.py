"""
LibreOffice Headless Engine
============================
`pptx_to_pdf.py` ve `pdf_to_docx.py` tarafından paylaşılan LibreOffice
tespit + subprocess dönüşüm mantığı. Önceden iki dosyada ayrı ayrı
kopyalanmıştı; kod tekrarını gidermek için tek yerden yönetilir.

SRP : Yalnızca LibreOffice headless süreciyle konuşmaktan sorumlu.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


def _profile_dir() -> Path:
    """
    Uygulamaya özel, kalıcı LibreOffice kullanıcı profili. Varsayılan profil
    paylaşılırsa kullanıcının açık LibreOffice penceresi dönüşüm isteklerini
    devralıyor: o pencere meşgulken (belge yüklüyor, diyalog açık) dönüşüm
    boş bir hatayla başarısız oluyor veya asılı kalıyor. Kalıcı olması, ilk
    çalıştırmadaki ~3 sn'lik profil oluşturma maliyetini yalnızca bir kez öder.
    """
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".cache")
    return Path(base) / "FileConvert" / "libreoffice_profile"


class LibreOfficeEngine:
    """LibreOffice headless ile dosya dönüştürme. Cross-platform."""

    _CANDIDATES: List[str] = [
        "libreoffice",
        "soffice",
        "/usr/lib/libreoffice/program/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    def __init__(self):
        self._path: Optional[str] = self._detect()

    def is_available(self) -> bool:
        return self._path is not None

    def convert_to(
        self,
        source_path: Path,
        output_path: Path,
        target_ext: str,
        extra_args: Optional[List[str]] = None,
    ) -> None:
        """
        Dönüşümü gerçekleştirir. Başarısızlıkta Exception fırlatır.
        target_ext nokta ile veya nokta olmadan verilebilir (örn. "pdf", ".docx").
        """
        out_dir = output_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = target_ext.lstrip(".")

        cmd = [
            self._path,
            "--headless",
            "--invisible",
            "--nologo",
            "--norestore",
            "-env:UserInstallation=" + _profile_dir().as_uri(),
            *(extra_args or []),
            "--convert-to", ext,
            "--outdir", str(out_dir),
            str(source_path),
        ]

        # Konsolsuz exe'de soffice.com gibi konsol başlatıcılar cmd penceresi açmasın.
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        stdout = result.stdout

        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice hatası (kod {result.returncode}):\n{result.stderr or stdout}"
            )

        lo_out = out_dir / (source_path.stem + f".{ext}")
        if not lo_out.exists():
            # Kaynak dizine mi düştü?
            fallback = source_path.parent / (source_path.stem + f".{ext}")
            if fallback.exists() and fallback != lo_out:
                shutil.move(str(fallback), str(lo_out))
            else:
                raise FileNotFoundError(
                    f"Dönüşüm sonrası dosya bulunamadı: {lo_out}\n"
                    f"LibreOffice çıktısı:\n{stdout}"
                )

        if lo_out != output_path:
            shutil.move(str(lo_out), str(output_path))

    @staticmethod
    def _detect() -> Optional[str]:
        for candidate in LibreOfficeEngine._CANDIDATES:
            found = shutil.which(candidate) or (
                Path(candidate).exists() and candidate
            )
            if found:
                return str(found)
        return None
