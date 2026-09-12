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

| # | Özellik | Neden | Efor | Not |
|---|---|---|---|---|
| 7 | **DOCX → PDF** | [[libreoffice-motoru]]'ndeki `LibreOfficeEngine.convert_to()` zaten iki yönlü çalışacak şekilde genel — şu an yalnızca PDF→DOCX yönü var, ters yön simetrik eksik. | Düşük | `LibreOfficeEngine` yeniden kullanılır, yeni `Strategy` bile gerekmez |
| 8 | **Çoklu görsel → tek çok-sayfalı PDF** | Mevcut `JpgToPdfConverter` her dosyayı **ayrı** tek-sayfalı PDF'e çeviriyor (1 girdi → 1 çıktı modeli). "10 fotoğrafı tek PDF'de birleştir" farklı bir kullanım şekli — N girdi → 1 çıktı. | Orta | `IConverter.convert()` imzası 1:1 varsayıyor; bu, ayrı bir "birleştirme modu" (yeni bir arayüz veya `MainWindow`'da özel bir yol) gerektirir — mimari genişleme noktası |
| 9 | **PDF sıkıştırma/optimize** | Kullanıcılar büyük PDF'leri küçültmek ister; PyMuPDF sayfa görüntülerini yeniden encode ederek boyut düşürebilir. | Orta | Yeni bir `PdfToPdfConverter` (aynı uzantı, farklı `display_name`) — registry `(source,target)` anahtarı `.pdf→.pdf` için de çalışır |
| 10 | **PDF birleştirme/bölme** | Sık istenen ofis işlevi. | Orta-Yüksek | Çoklu-dosya→tek-dosya (madde 8 ile aynı mimari genişleme ihtiyacı) |
| 11 | **Paralel toplu dönüşüm** | `core/conversion_facade.convert_batch()` şu an dosyaları sırayla işliyor; LibreOffice/PyMuPDF çağrıları I/O-bound, bağımsız dosyalarda paralellikten fayda görür. | Orta | **Dikkat**: LibreOffice headless tek seferde tek `soffice` sürecini güvenilir paylaşamayabilir (soket/profil çakışması) — önce PyMuPDF-tabanlı converter'larda (PDF→JPG, JPG→PDF) paralellik denenmeli, LibreOffice'li olanlarda temkinli ilerlenmeli |
| 12 | **Klasör sürükle-bırak (recursive)** | Şu an yalnızca tekil dosyalar kabul ediliyor; kullanıcı bir klasörü sürükleyip içindeki uygun dosyaların otomatik toplanmasını bekleyebilir. | Düşük-Orta | `DropZoneWidget.dropEvent()`'e dizin tarama eklenir |
| 13 | **Açık/koyu tema geçişi** | `ui/styles/theme.py`'deki `PALETTE` zaten merkezi tek sözlük — ikinci bir palet + `QSettings`'te tercih saklamak yeterli. | Orta | Şu an tek `MAIN_STYLE` string'i `PALETTE`'e bağlı; iki palet arası geçiş için stil yeniden üretimi gerekir |

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

Kademe 1 tamamlandı. Bir sonraki iterasyon için Kademe 2'den madde 7
(DOCX→PDF, neredeyse bedava — `LibreOfficeEngine` zaten iki yönlü) ve
madde 12 (klasör sürükle-bırak) önerilir. Madde 14 (CLI modu) ayrı bir
"v2.1" olarak planlanabilir — mimari zaten hazır olduğu için üzerinde
acele etmeye gerek yok, ama düşük riskli/yüksek sembolik değerli bir
sonraki adım (backend/frontend ayrımının pratikte kanıtı — [[paketleme]]
ile birlikte, artık gerçek bir exe üzerinden de gösterilebilir).

Kademe 2/3'teki N-girdi→1-çıktı gerektiren maddeler (8, 10) mevcut
`IConverter.convert(source_path, options) -> ConversionResult` imzasının
1:1 varsayımını zorluyor — bunlara girişmeden önce ayrı bir mimari
tasarım turu (yeni bir arayüz mü, yoksa `MainWindow`'da özel bir yol mu)
gerekir; bu rapor kapsamında karar verilmedi, yalnızca fırsat olarak not
edildi.

## İlgili Sayfalar

- [[mimari]] — bu önerilerin oturduğu temel
- [[converter-arayuzu]] — 1:1 varsayımının kaynağı (madde 8/10 notu)
- [[converter-ekleme]] — Kademe 1/2'deki yeni converter'ların ekleneceği yer
- [[rules]] — hangi kurallara uyarak eklenecekleri
