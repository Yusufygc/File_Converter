"""
PyMuPDF Araç Tabanı
=====================
Döndür, Filigran, Sayfa Numarası, Şifrele, Şifre Kaldır, Onar gibi
`.pdf`→`.pdf` araçları; motor tespiti, kurulum ipucu, paralel güvenliği
ve "kaynağın üzerine yazmamak için sonek ekle" çıktı yolu bakımından
birebir aynı. Bunları her dosyada kopyalamak yerine tek tabanda toplar.

Taban kasıtlı olarak `source_extension`/`target_extension`/`display_name`'i
implemente ETMEZ — `SimpleLibreOfficeConverter` gibi abstract kalır ve
`discovery.py` tarafından somut converter sanılmaz (bkz. docs/wiki/converter-arayuzu.md).

SRP : PyMuPDF tabanlı araçların ortak altyapısından sorumlu.
"""

from __future__ import annotations

from pathlib import Path

from core.converters.base import BaseConverter
from core.interfaces.converter_interface import ConversionOptions
from core.user_texts import ENGINE_BUILTIN, ENGINE_UNAVAILABLE, HINT_BUILTIN_MISSING


class PyMuPdfToolConverter(BaseConverter):
    """Kaynak ile aynı uzantıda çıktı üreten PyMuPDF araçları için taban."""

    # Alt sınıf override eder. Kaynak ve hedef uzantı aynı olduğunda sonek
    # olmadan varsayılan çıktı klasöründe kaynağın üzerine yazılırdı.
    output_suffix: str = "_islenmis"

    def get_output_path(self, source_path: Path, options: ConversionOptions) -> Path:
        out_dir = options.output_dir or source_path.parent
        return out_dir / f"{source_path.stem}{self.output_suffix}{self.target_extension}"

    @property
    def unavailable_hint(self) -> str:
        return HINT_BUILTIN_MISSING

    @property
    def is_available(self) -> bool:
        try:
            import fitz  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def active_engine_name(self) -> str:
        return ENGINE_BUILTIN if self.is_available else ENGINE_UNAVAILABLE

    @property
    def is_parallel_safe(self) -> bool:
        # Yalnızca PyMuPDF kullanır — dış süreç/paylaşımlı durum yok.
        return True
