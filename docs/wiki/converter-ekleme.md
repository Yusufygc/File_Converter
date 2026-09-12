# Yeni Converter Ekleme

Bu proje tak-çıkar (plug-in) mimariye sahiptir: yeni bir dönüşüm türü
eklemenin **tek adımı**, `core/converters/` içine bir dosya eklemektir.
`ui/main_window.py` ve `ui/widgets/options_panel.py`'ye **dokunulmaz** —
bkz. [[mimari]].

## Adımlar

1. `core/converters/` altına yeni bir dosya aç, [[converter-arayuzu]]'ndeki
   `BaseConverter`'ı türet:

```python
# core/converters/docx_to_pdf.py
from pathlib import Path
from typing import Optional
from core.converters.base import BaseConverter, ConvertOutcome
from core.interfaces.converter_interface import ConversionOptions

class DocxToPdfConverter(BaseConverter):
    @property
    def source_extension(self) -> str: return ".docx"
    @property
    def target_extension(self) -> str: return ".pdf"
    @property
    def display_name(self) -> str: return "Word → PDF"
    @property
    def is_available(self) -> bool: return True
    @property
    def active_engine_name(self) -> str: return "libreoffice"
    @property
    def unavailable_hint(self) -> str: return "pip install ..."

    def _do_convert(self, source_path: Path, output_path: Path, options: ConversionOptions) -> Optional[ConvertOutcome]:
        ...  # asıl dönüşüm mantığı; hata durumunda Exception fırlat
        return None
```

2. Bu kadar. `core/converters/discovery.py`, paketi `pkgutil` ile tarar,
   somut (abstract olmayan) `IConverter` alt sınıflarını bulur,
   `MainWindow.__init__()`'te otomatik `registry`'ye kaydeder.
3. `ui/converter_catalog.py`, `registry.all_converters()`'dan dropdown
   listesini üretir — yeni converter otomatik görünür.

## Görünüm Sırası (opsiyonel)

Dropdown'daki sıra `ui/converter_catalog.py`'deki `_PREFERRED_ORDER`
listesinden gelir. Bu **fonksiyonel bir gereklilik değildir** —
listede olmayan bir converter alfabetik olarak sona eklenir, yani bu
adımı atlasan da converter doğru çalışır, yalnızca dropdown'da en sonda
görünür. İstersen `(source_ext, target_ext)` çiftini oraya da ekleyebilirsin.

## Birden Fazla Motor Gerekiyorsa

Converter'ın MS Office/LibreOffice gibi birden fazla gerçek motoru varsa
ve kullanıcı elle seçim yapabilmeli ise, `IEngineSelectable` protokolünü
de implemente et (bkz. [[converter-arayuzu]]) — `PptxToPdfConverter` örnek
alınabilir. LibreOffice motoruna ihtiyaç varsa `core/converters/libreoffice_engine.py`
içindeki paylaşılan `LibreOfficeEngine`'i kullan, yeniden yazma —
bkz. [[libreoffice-motoru]].

## Test Ekle

`core/`'a eklenen her yeni dönüşüm mantığı için `tests/` altına Qt
gerektirmeyen bir pytest testi eklenir — bkz. [[test-ve-bagimliliklar]] ve
[[rules]].

## Doğrulama

Eklemenin gerçekten "dokunmadan çalıştığını" kanıtlamak için: uygulamayı
başlat (`python main.py`), yeni converter'ın dropdown'da göründüğünü
gözle; ya da headless bir Qt script'iyle `registry.all_converters()`
sayısını kontrol et (bu oturumda tam olarak bu yöntemle doğrulandı).

## İlgili Sayfalar

- [[converter-arayuzu]] — implemente edilecek sözleşme
- [[donusturucu-envanteri]] — mevcut converter'lardan örnekler
- [[mimari]] — bu mekanizmanın genel akıştaki yeri
