# FileConvert Pro

PySide6 ile yazılmış profesyonel dosya dönüştürücü uygulaması.

---

## Kurulum

```bash
pip install PySide6

# PPTX→PDF için LibreOffice gereklidir:
# Ubuntu/Debian:
sudo apt install libreoffice

# Windows: https://www.libreoffice.org/download
```

## Çalıştırma

```bash
cd fileconverter
python main.py
```

---

## Proje Mimarisi

```
fileconverter/
│
├── main.py                          # Giriş noktası, Composition Root
│
├── core/                            # Domain katmanı (UI'dan bağımsız)
│   ├── interfaces/
│   │   └── converter_interface.py   # IConverter, IConverterRegistry sözleşmeleri
│   └── converters/
│       ├── registry.py              # ConverterRegistry (OCP uyumlu)
│       └── pptx_to_pdf.py           # PptxToPdfConverter implementasyonu
│
├── services/                        # Uygulama servis katmanı
│   └── conversion_service.py        # ConversionService + ConversionWorker (QThread)
│
└── ui/                              # Sunum katmanı
    ├── main_window.py               # MainWindow (Controller)
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
| **SRP** | Her sınıf tek sorumluluğa sahip: `DropZoneWidget` yalnızca dosya alır, `ConversionService` yalnızca iş akışını yönetir |
| **OCP** | `IConverter`'ı implement eden yeni bir sınıf ekleyerek sistemi genişletebilirsiniz, mevcut kod değişmez |
| **LSP** | Tüm `IConverter` implementasyonları aynı sözleşmeyle çalışır, birbirinin yerine geçebilir |
| **ISP** | `IConverter` ve `IConverterRegistry` ayrı, küçük interface'ler |
| **DIP** | `ConversionService`, `PptxToPdfConverter`'a değil `IConverter` soyutlamasına bağımlı |

---

## Yeni Converter Ekleme

```python
# core/converters/docx_to_pdf.py
from core.interfaces.converter_interface import IConverter, ConversionOptions, ConversionResult

class DocxToPdfConverter(IConverter):
    @property
    def source_extension(self) -> str: return ".docx"
    @property
    def target_extension(self) -> str: return ".pdf"
    @property
    def display_name(self) -> str: return "Word → PDF"
    
    def validate(self, source_path): ...
    def convert(self, source_path, options): ...

# main.py'de:
registry.register(DocxToPdfConverter())
# Başka hiçbir kod değişmez.
```
