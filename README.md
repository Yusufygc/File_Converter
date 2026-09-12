# FileConvert Pro

PySide6 ile yazılmış profesyonel dosya dönüştürücü uygulaması.

---

## Kurulum

```bash
pip install -r requirements.txt

# Geliştirme (testler dahil):
pip install -r requirements-dev.txt

# PPTX→PDF ve PDF→DOCX/ODT için LibreOffice gereklidir:
# Ubuntu/Debian:
sudo apt install libreoffice

# Windows: https://www.libreoffice.org/download
```

## Çalıştırma

```bash
cd fileconverter
python main.py
```

## Testler

```bash
python -m pytest tests/ -v
```

`core/` katmanı hiç Qt bağımlılığı taşımadığı için testler PySide6
başlatmadan, milisaniyeler içinde çalışır.

---

## Proje Mimarisi

Backend (`core/`) ve frontend (`ui/`) fiziksel olarak ayrılmıştır:
`core/` hiçbir Qt importu içermez, tak-çıkar (plug-in) bir converter
mimarisi kullanır.

```
fileconverter/
│
├── main.py                          # Giriş noktası
├── conftest.py                      # pytest için proje kökünü sys.path'e ekler
│
├── core/                            # Backend — %100 framework-agnostic, hiç Qt import etmez
│   ├── interfaces/
│   │   ├── converter_interface.py   # IConverter, IConverterRegistry sözleşmeleri
│   │   └── engine_interface.py      # IEngineSelectable (opsiyonel "motor seçilebilir" capability)
│   ├── converters/
│   │   ├── base.py                  # BaseConverter — ortak validate/timing/hata iskeleti (template method)
│   │   ├── discovery.py             # Paketi otomatik tarar, IConverter alt sınıflarını registry'ye kaydeder
│   │   ├── registry.py              # ConverterRegistry
│   │   ├── libreoffice_engine.py    # Paylaşılan LibreOffice headless motoru
│   │   ├── pptx_to_pdf.py           # PptxToPdfConverter (MS Office / LibreOffice)
│   │   ├── pdf_to_docx.py           # PdfToDocxConverter + PdfToOdtConverter
│   │   ├── pdf_to_jpg.py            # PdfToJpgConverter (PyMuPDF)
│   │   └── jpg_to_pdf.py            # JpgToPdfConverter (PyMuPDF)
│   └── conversion_facade.py         # convert_batch() — senkron, Qt'siz backend API'si
│
├── tests/                           # core/ için pytest testleri (Qt gerektirmez)
│
└── ui/                              # Frontend — %100 PySide6
    ├── main_window.py               # MainWindow (Controller / Composition Root)
    ├── converter_catalog.py         # registry'den dropdown listesini JENERİK üretir
    ├── adapters/
    │   └── qt_conversion_runner.py  # convert_batch()'i QThread içinde çalıştırır
    ├── styles/
    │   └── theme.py                 # Merkezi tema/renk sabitleri
    ├── widgets/
    │   ├── drop_zone.py             # Sürükle-bırak alanı
    │   ├── file_list.py             # Dosya listesi + durum göstergesi
    │   └── options_panel.py         # Seçenek paneli
    └── dialogs/
        └── summary_dialog.py        # Dönüşüm özet diyaloğu
```

---

## SOLID Prensipleri

| Prensip | Uygulama |
|---------|----------|
| **SRP** | `DropZoneWidget` yalnızca dosya alır, `BaseConverter` yalnızca ortak dönüşüm akışını yönetir, `QtConversionRunner` yalnızca Qt thread orkestrasyonundan sorumlu |
| **OCP** | `IConverter`'ı implement eden yeni bir dosya `core/converters/`'a eklenir eklenmez `discovery.py` otomatik bulur ve kaydeder — mevcut kod (main_window, options_panel) değişmez |
| **LSP** | Tüm `IConverter` implementasyonları aynı sözleşmeyle çalışır, birbirinin yerine geçebilir |
| **ISP** | `IConverter`, `IConverterRegistry`, `IEngineSelectable` ayrı, küçük interface'ler — motor seçimi yalnızca ihtiyacı olan converter'ların implemente ettiği opsiyonel bir capability |
| **DIP** | `QtConversionRunner` ve `convert_batch()`, somut converter sınıflarına değil `IConverter` soyutlamasına bağımlı |

---

## Yeni Converter Ekleme

Tek adım: `core/converters/` içine `BaseConverter`'ı implement eden bir
dosya ekle. `main_window.py`/`options_panel.py`'ye dokunmaya gerek yok —
otomatik keşif (`discovery.py`) dropdown'da otomatik görünmesini sağlar.

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
        ...  # asıl dönüşüm mantığı
        return None

# Başka hiçbir kod değişmez — dosyayı eklemek yeterli.
```
