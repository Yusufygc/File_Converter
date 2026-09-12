# Yol Haritası — Yeni Versiyon Öneri Raporu

Mevcut mimari ([[mimari]], [[converter-arayuzu]]) tak-çıkar converter
sistemi + Qt'siz `core/` üzerine kurulu olduğu için, aşağıdaki öneriler
bu temele **ne kadar az sürtünmeyle oturduğuna** göre 3 kademeye
ayrılmıştır. Her madde: ne, neden, efor, mimari not.

## Kademe 1 — Hızlı Kazanımlar (mevcut mimariye birebir oturur)

**Durum: ✅ Tamamlandı** (bkz. [[log]]). Aşağıdaki tablo orijinal öneri
metniyle birlikte, her maddenin gerçekte nasıl çözüldüğünü gösteriyor.

| # | Özellik | Neden | Sonuç |
|---|---|---|---|
| 1 | **İptal butonu** | `QtConversionRunner.cancel()` zaten yazılıydı ama UI'a bağlı değildi. | ✅ Tek buton (Dönüştür ↔ İptal Et) toggle olarak eklendi — bkz. [[ui-katmani]] |
| 2 | **PDF → PNG** | `PdfToJpgConverter`'ın kayıpsız format kardeşi. | ✅ `PdfToPngConverter` eklendi — bkz. [[donusturucu-envanteri]] |
| 3 | **Dosya türü ikonları** | `FileItemWidget` her zaman `file_pptx.svg` gösteriyordu. | ✅ `ui/icon_map.py` + `file_jpg.svg`/`file_generic.svg` eklendi — bkz. [[ui-katmani]] |
| 4 | **Ayarları hatırlama (QSettings)** | Son çıktı klasörü, pencere boyutu, son seçilen dönüşüm türü her açılışta sıfırlanıyordu. | ✅ `ui/app_settings.py` (`AppSettings`) eklendi — bkz. [[ui-katmani]] |
| 5 | **PyInstaller paketleme** | `resource_helper.py` `_MEIPASS`'e hazırdı ama hiç `.spec` dosyası yoktu. | ✅ `fileconvert.spec` eklendi, gerçek bir build ile doğrulandı — bkz. [[paketleme]] |
| 6 | **CI (GitHub Actions)** | Testler otomatik tetiklenmiyordu. | ✅ `.github/workflows/test.yml` eklendi — bkz. [[test-ve-bagimliliklar]] |

## Kademe 2 — Orta Vadeli (yeni converter'lar + orkestrasyon)

**Durum: Güvenli 4 madde (7, 9, 12, 13) tamamlandı** — bkz. [[log]].
Madde 8, 10, 11 **kullanıcı kararıyla ertelendi**: mevcut
`IConverter.convert(source_path, options) -> ConversionResult`
imzasının "1 girdi → 1 çıktı" varsayımını zorluyor (8, 10) veya
LibreOffice eşzamanlılık riski taşıyor (11) — ayrı bir mimari tasarım
turu gerektiriyorlar, bu turun kapsamına bilinçli olarak alınmadı.

| # | Özellik | Neden | Sonuç |
|---|---|---|---|
| 7 | **DOCX → PDF** | `LibreOfficeEngine.convert_to()` zaten iki yönlü çalışacak şekilde genel. | ✅ `DocxToPdfConverter` eklendi — bkz. [[donusturucu-envanteri]] |
| 8 | **Çoklu görsel → tek çok-sayfalı PDF** | N girdi → 1 çıktı, mevcut 1:1 imzayı zorluyor. | ⏸️ **Ertelendi** — ayrı mimari tasarım turu gerekiyor |
| 9 | **PDF sıkıştırma/optimize** | Kullanıcılar büyük PDF'leri küçültmek ister. | ✅ `PdfCompressConverter` eklendi (PyMuPDF `deflate`/`garbage` bayrakları, rasterize etmeden) |
| 10 | **PDF birleştirme/bölme** | N:1/1:N, madde 8 ile aynı mimari ihtiyaç. | ⏸️ **Ertelendi** — ayrı mimari tasarım turu gerekiyor |
| 11 | **Paralel toplu dönüşüm** | LibreOffice eşzamanlılık riski. | ⏸️ **Ertelendi** — ayrı risk değerlendirmesi gerekiyor |
| 12 | **Klasör sürükle-bırak (recursive)** | Yalnızca tekil dosyalar kabul ediliyordu. | ✅ `ui/file_discovery.py` (`collect_files()`) + `DropZoneWidget` güncellendi |
| 13 | **Açık/koyu tema geçişi** | `PALETTE` merkezi tek sözlük, ikinci bir palet eklemek mantıklı. | ✅ `LIGHT_PALETTE` + `AppSettings` tema tercihi eklendi — **yeniden başlatınca uygulanır** (canlı geçiş değil, bkz. [[ui-katmani]]) |

## Kademe 3 — Büyük / Stratejik (mimari zaten hazır, ayrı planlama gerekir)

| # | Özellik | Neden | Efor | Not |
|---|---|---|---|---|
| 14 | **CLI modu** | `core/conversion_facade.py` **tam olarak bunun için** Qt'siz tasarlandı (bkz. [[mimari]]) — şu an yalnızca `ui/` bunu çağırıyor. `fileconvert convert giris.pdf --hedef jpg` gibi bir komut satırı arayüzü, mimarinin doğal bir sonraki adımı. | Orta | Yeni bir `cli.py` (argparse/click) + `core.converters.discovery`/`conversion_facade` — `ui/`'a hiç dokunmadan eklenebilir, ayrım tam olarak bunu kanıtlıyor |
| 15 | **OCR desteği (taranmış PDF)** | `pdf2docx` şu an taranmış PDF'lerde "0 kelime, muhtemelen taranmış" uyarısı veriyor ve sessizce boş sonuç üretiyor (mevcut kodda zaten bu log var). Tesseract/`pytesseract` ile OCR katmanı eklenirse bu senaryo gerçek destek kazanır. | Yüksek | Yeni bir harici bağımlılık (Tesseract binary) + [[donusturucu-envanteri]]'ne yeni satır |
| 16 | **Şifreli PDF desteği** | Parola korumalı PDF'ler şu an muhtemelen sessizce/hata ile başarısız oluyor; parola sorma akışı eklenmedi. | Orta | `ConversionOptions`'a opsiyonel `password` alanı + PyMuPDF/`pdf2docx`'in şifre API'leri |
| 17 | **Harici plugin klasörü** | `core/converters/discovery.py` şu an yalnızca kendi paketini tarıyor (bkz. [[converter-ekleme]]). Kullanıcı bilgisayarındaki ayrı bir klasörü (örn. `%APPDATA%/FileConvertPro/plugins/`) de tarayacak şekilde genişletilirse gerçek 3.-parti eklenti dağıtımı mümkün olur. | Yüksek | Güvenlik notu: dış klasörden keyfi Python kodu çalıştırmak güven sınırını genişletir, imzalama/sandbox tartışılmalı |
| 18 | **Windows Gezgini sağ-tık entegrasyonu** | "Dosyaya sağ tıkla → FileConvert Pro ile dönüştür" — masaüstü uygulaması için doğal beklenti. | Yüksek | Registry shell extension, platform-specific, paketleme (madde 5) sonrası anlamlı |
| 19 | **Çoklu dil (i18n)** | Şu an tüm UI metni Türkçe hardcoded (bkz. [[rules]] — proje dili Türkçe). Uluslararası kullanıcı hedefleniyorsa Qt `QTranslator` ile ayrıştırma gerekir. | Yüksek | Büyük bir string-çıkarma emeği; yalnızca gerçekten ihtiyaç varsa önerilir |

## Önerilen "Sonraki Versiyon" Kapsamı

Kademe 1 ve Kademe 2'nin güvenli 4 maddesi (7, 9, 12, 13) tamamlandı.
Bundan sonraki iki gerçek seçenek:

1. **Madde 14 (CLI modu)** — mimari zaten hazır (`core/conversion_facade.py`
   Qt'siz), düşük riskli/yüksek sembolik değerli bir adım
   (backend/frontend ayrımının pratikte kanıtı — [[paketleme]] ile
   birlikte artık gerçek bir exe üzerinden de gösterilebiliyor).
2. **N:1 mimari tasarım turu** — madde 8 (çoklu görsel→tek PDF) ve
   madde 10'u (PDF birleştirme/bölme) gerçekten çözmek isteniyorsa,
   `IConverter.convert(source_path, options) -> ConversionResult`
   imzasının 1:1 varsayımını genişletmek için ayrı, odaklı bir tasarım
   oturumu gerekir (yeni bir arayüz mü, yoksa `MainWindow`'da özel bir
   yol mu — bu rapor kapsamında karar verilmedi).

Madde 11 (paralel dönüşüm) için ayrı bir risk değerlendirmesi
(özellikle LibreOffice eşzamanlılığı) önerilir, tek başına ele
alınabilir.

## İlgili Sayfalar

- [[mimari]] — bu önerilerin oturduğu temel
- [[converter-arayuzu]] — 1:1 varsayımının kaynağı (madde 8/10 notu)
- [[converter-ekleme]] — Kademe 1/2'deki yeni converter'ların ekleneceği yer
- [[rules]] — hangi kurallara uyarak eklenecekleri
