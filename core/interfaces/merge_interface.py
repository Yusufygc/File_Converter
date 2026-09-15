"""
Merge Capable
==============
Birden fazla dosyayı TEK bir çıktıda birleştirebilen converter'lar için
opsiyonel capability protokolü (örn. birden çok JPG'yi tek çok sayfalı
PDF'e, veya birden çok PDF'i tek PDF'e birleştirme). UI, bir converter'ın
"birleştirme modu" sunup sunmadığını `isinstance(converter, IMergeConverter)`
ile anlar — `IEngineSelectable` (`engine_interface.py`) ile aynı desen.

`core/converters/base.py`'daki `MergeCapableConverter`, bu protokolü
karşılayan somut converter'ların türediği ortak temel sınıftır —
yalnızca onu extend eden sınıflarda `convert_many` var olur, bu yüzden
isinstance kontrolü yanlış pozitif vermez (düz `BaseConverter` alt
sınıflarında `convert_many` hiç yoktur).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Protocol, runtime_checkable

from core.interfaces.converter_interface import ConversionOptions, ConversionResult


@runtime_checkable
class IMergeConverter(Protocol):
    def convert_many(
        self,
        source_paths: List[Path],
        options: ConversionOptions,
    ) -> ConversionResult: ...
