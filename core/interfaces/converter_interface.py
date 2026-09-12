"""
Converter Interface Module
==========================
SOLID Principles:
  - ISP: Interface Segregation — küçük, odaklı interface'ler
  - DIP: Dependency Inversion — somut implementasyona değil soyutlamaya bağımlı
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ConversionOptions:
    """Dönüşüm seçeneklerini kapsayan değer nesnesi (Value Object)."""
    output_dir: Optional[Path] = None
    dpi: int = 150
    quality: int = 90
    overwrite_existing: bool = True

    def __post_init__(self):
        if self.dpi < 72 or self.dpi > 600:
            raise ValueError("DPI değeri 72-600 arasında olmalıdır.")
        if self.quality < 1 or self.quality > 100:
            raise ValueError("Kalite değeri 1-100 arasında olmalıdır.")


@dataclass
class ConversionResult:
    """Tek bir dosya dönüşümünün sonucunu temsil eder."""
    source_path: Path
    output_path: Optional[Path]
    success: bool
    error_message: str = ""
    page_count: int = 0
    elapsed_seconds: float = 0.0

    @property
    def file_name(self) -> str:
        return self.source_path.name


@dataclass
class BatchConversionResult:
    """Toplu dönüşüm sonuçlarını özetler."""
    results: List[ConversionResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        return self.total - self.success_count

    @property
    def all_succeeded(self) -> bool:
        return self.failure_count == 0


class IConverter(ABC):
    """
    Tüm dosya dönüştürücüler için temel sözleşme.
    OCP: Yeni dönüştürücüler bu arayüzü implement ederek eklenir,
         mevcut kod değiştirilmez.
    """

    @property
    @abstractmethod
    def source_extension(self) -> str:
        """Kaynak dosya uzantısı (örn: '.pptx')"""

    @property
    @abstractmethod
    def target_extension(self) -> str:
        """Hedef dosya uzantısı (örn: '.pdf')"""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Kullanıcıya gösterilecek dönüşüm adı (örn: 'PPTX → PDF')"""

    @property
    def accepted_extensions(self) -> List[str]:
        """
        Kabul edilen kaynak dosya uzantıları.
        Varsayılan: yalnızca `source_extension`. Birden çok uzantı kabul
        eden converter'lar (örn. .jpg + .jpeg) bunu override eder.
        UI (drop zone, dosya diyaloğu) bunu okuyarak filtre kurar.
        """
        return [self.source_extension]

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Bu dönüşüm için gerekli motor/araç sistemde kurulu/erişilebilir mi."""

    @property
    @abstractmethod
    def active_engine_name(self) -> str:
        """UI'da gösterilecek aktif motor adı (örn. 'LibreOffice', 'PyMuPDF')."""

    @abstractmethod
    def validate(self, source_path: Path) -> bool:
        """Kaynak dosyanın bu dönüştürücü ile uyumlu olduğunu doğrular."""

    @abstractmethod
    def convert(
        self,
        source_path: Path,
        options: ConversionOptions,
    ) -> ConversionResult:
        """
        Tek bir dosyayı dönüştürür.
        Thread-safe olmalı (QThread içinden çağrılır).
        """

    def get_output_path(self, source_path: Path, options: ConversionOptions) -> Path:
        """Çıktı dosyasının tam yolunu hesaplar."""
        out_dir = options.output_dir or source_path.parent
        return out_dir / (source_path.stem + self.target_extension)


class IConverterRegistry(ABC):
    """Converter kayıt defteri sözleşmesi."""

    @abstractmethod
    def register(self, converter: IConverter) -> None:
        """Yeni bir converter kaydeder."""

    @abstractmethod
    def get(self, source_ext: str, target_ext: str) -> Optional[IConverter]:
        """Uzantı çiftine göre converter döndürür."""

    @abstractmethod
    def all_converters(self) -> List[IConverter]:
        """Tüm kayıtlı converter'ları listeler."""
