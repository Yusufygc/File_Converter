"""
Base Converter — Template Method
=================================
Tüm converter'ların ortak iskeletini (validate + is_available kontrolü +
zamanlama + try/except + ConversionResult üretimi) tek yerde toplar.
Önceden her converter dosyasında ayrı ayrı kopyalanan bu iskelet, artık
alt sınıflar yalnızca `_do_convert()` (ve `_unavailable_message()`)
implemente ederek yeniden yazılmıyor.

SRP : Ortak dönüşüm akışından sorumlu, dönüşümün kendisinden değil.
"""

from __future__ import annotations

import time
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from core.interfaces.converter_interface import (
    ConversionOptions,
    ConversionResult,
    IConverter,
)


@dataclass
class ConvertOutcome:
    """
    `_do_convert()` başarı sonucunu taşır.
    Alanlar opsiyoneldir — verilmezse şablon metodun hesapladığı
    varsayılan `output_path` ve `page_count=0` kullanılır.
    """
    output_path: Optional[Path] = None
    page_count: int = 0


class BaseConverter(IConverter):
    """Ortak `convert()` akışını sağlayan şablon sınıf."""

    def validate(self, source_path: Path) -> bool:
        return (
            source_path.exists()
            and source_path.is_file()
            and source_path.suffix.lower() in self.accepted_extensions
        )

    def convert(
        self,
        source_path: Path,
        options: ConversionOptions,
    ) -> ConversionResult:
        start = time.monotonic()

        if not self.validate(source_path):
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=f"Geçersiz dosya: {source_path.name}",
                elapsed_seconds=time.monotonic() - start,
            )

        if not self.is_available:
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=self.unavailable_hint,
                elapsed_seconds=time.monotonic() - start,
            )

        output_path = self.get_output_path(source_path, options)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            outcome = self._do_convert(source_path, output_path, options) or ConvertOutcome()
            return ConversionResult(
                source_path=source_path,
                output_path=outcome.output_path or output_path,
                success=True,
                page_count=outcome.page_count,
                elapsed_seconds=time.monotonic() - start,
            )
        except Exception as exc:
            return ConversionResult(
                source_path=source_path,
                output_path=None,
                success=False,
                error_message=str(exc),
                elapsed_seconds=time.monotonic() - start,
            )

    # ------------------------------------------------------------------ #
    #  Alt sınıfların implemente etmesi gereken hook'lar                   #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def _do_convert(
        self,
        source_path: Path,
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        """
        Asıl dönüşüm mantığı. Başarısızlıkta Exception fırlatır.
        None dönerse output_path/page_count varsayılanları kullanılır.
        """

    @property
    @abstractmethod
    def unavailable_hint(self) -> str:
        """
        `is_available` False iken kullanıcıya gösterilecek kurulum ipucu.
        Public — UI (main_window) motoru kurulu değilse bu metni doğrudan
        okuyabilir, dönüşüm türüne göre hardcoded metin tutmasına gerek kalmaz.
        """


class MergeCapableConverter(BaseConverter):
    """
    Birden fazla dosyayı TEK bir çıktıda birleştirebilen converter'lar
    için `convert_many()` şablon metodunu ekler (`IMergeConverter`
    capability'sinin somutlaştığı yer).

    Bilinçli olarak `BaseConverter`'ın kendisine değil, ayrı bir alt
    sınıfa eklenir: `convert_many`'i doğrudan `BaseConverter`'a koymak
    TÜM converter'lara bu metodu miras bırakırdı (çağrılmasa bile
    *var olurdu*) — bu da `isinstance(x, IMergeConverter)` kontrolünü
    her converter için `True` yapıp capability deseni bozardı. Yalnızca
    bunu extend eden sınıflarda `convert_many` var olur.
    """

    def convert_many(
        self,
        source_paths: List[Path],
        options: ConversionOptions,
    ) -> ConversionResult:
        start = time.monotonic()

        valid = [p for p in source_paths if self.validate(p)]
        if not valid:
            return ConversionResult(
                source_path=source_paths[0] if source_paths else Path("."),
                output_path=None,
                success=False,
                error_message="Geçerli dosya bulunamadı.",
                elapsed_seconds=time.monotonic() - start,
            )

        if not self.is_available:
            return ConversionResult(
                source_path=valid[0],
                output_path=None,
                success=False,
                error_message=self.unavailable_hint,
                elapsed_seconds=time.monotonic() - start,
            )

        out_dir = options.output_dir or valid[0].parent
        output_path = out_dir / f"{valid[0].stem}_birlesik{self.target_extension}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            outcome = self._do_convert_many(valid, output_path, options) or ConvertOutcome()
            return ConversionResult(
                source_path=valid[0],
                output_path=outcome.output_path or output_path,
                success=True,
                page_count=outcome.page_count,
                elapsed_seconds=time.monotonic() - start,
            )
        except Exception as exc:
            return ConversionResult(
                source_path=valid[0],
                output_path=None,
                success=False,
                error_message=str(exc),
                elapsed_seconds=time.monotonic() - start,
            )

    @abstractmethod
    def _do_convert_many(
        self,
        source_paths: List[Path],
        output_path: Path,
        options: ConversionOptions,
    ) -> Optional[ConvertOutcome]:
        """
        Birleştirme mantığı. `source_paths` en az bir geçerli dosya
        içerir (boş/geçersiz olanlar zaten elenmiştir). Başarısızlıkta
        Exception fırlatır.
        """
