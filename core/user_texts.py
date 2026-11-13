"""
Kullanıcıya Gösterilen Ortak Metinler
=======================================
Converter'ların `active_engine_name` ve `unavailable_hint` değerleri
doğrudan UI'da görünür. Önceden her converter kendi metnini yazıyordu ve
kütüphane adları (PyMuPDF, pdf2docx, pymupdf4llm) ile geliştirici
komutları (`pip install`, `apt`, `brew`, `winget`) kullanıcıya sızıyordu.

Kural: kullanıcının **kendisinin kurabileceği programlar** (LibreOffice,
Microsoft Office, Tesseract) adıyla anılır ve indirme bağlantısı verilir;
uygulamayla birlikte gelen kütüphaneler "Yerleşik" olarak gösterilir ve
eksiklerse yeniden kurulum önerilir — kullanıcı onları ayrıca kuramaz.

SRP : Yalnızca ortak kullanıcı metinlerinden sorumlu.
"""

# ── Etkin dönüştürme yöntemi etiketleri (`active_engine_name`) ──────────
ENGINE_BUILTIN = "Yerleşik"
ENGINE_BUILTIN_WITH_OCR = "Yerleşik + Metin tanıma"
ENGINE_LIBREOFFICE = "LibreOffice"
ENGINE_MS_OFFICE = "Microsoft Office"
ENGINE_OCR = "Metin tanıma"
ENGINE_IMAGE_EMBED = "Görsel olarak aktarma"
ENGINE_UNAVAILABLE = "Kullanılamıyor"

# ── Kurulum ipuçları (`unavailable_hint`) ────────────────────────────────
LIBREOFFICE_URL = "https://www.libreoffice.org/download"
TESSERACT_URL = "https://github.com/UB-Mannheim/tesseract/wiki"

HINT_BUILTIN_MISSING = (
    "Uygulamanın bu dönüşüm için gereken bir bileşeni eksik veya bozuk.\n\n"
    "FileConvert'ü yeniden kurmayı deneyin."
)

HINT_LIBREOFFICE = (
    "Bu dönüşüm için ücretsiz LibreOffice programı gerekiyor.\n\n"
    f"İndirme: {LIBREOFFICE_URL}\n"
    "Kurduktan sonra FileConvert'ü yeniden başlatın."
)

HINT_OFFICE_OR_LIBREOFFICE = (
    "Bu dönüşüm için Microsoft Office veya ücretsiz LibreOffice programı gerekiyor.\n\n"
    f"LibreOffice indirme: {LIBREOFFICE_URL}\n"
    "Kurduktan sonra FileConvert'ü yeniden başlatın."
)

HINT_TESSERACT = (
    "Bu işlem için ücretsiz Tesseract metin tanıma programı gerekiyor.\n\n"
    f"İndirme: {TESSERACT_URL}\n"
    "Kurulumda Türkçe dil paketini seçin, ardından FileConvert'ü yeniden başlatın."
)
