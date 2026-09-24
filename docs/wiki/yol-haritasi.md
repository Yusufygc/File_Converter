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

**Durum: ✅ 7 maddenin tamamı tamamlandı** — bkz. [[log]]. Madde 8/10
başta N:1 mimari genişlemesi gerektirdiği için, madde 11 de LibreOffice
eşzamanlılık riski nedeniyle ilk turda ertelenmişti; ikinci bir
tasarım turunda çözüldü: `IMergeConverter` (`IEngineSelectable` ile
aynı desende opsiyonel capability) mevcut 1:1 `convert()` akışına HİÇ
dokunmadan N:1'i ekledi; paralel dönüşüm yalnızca `is_parallel_safe=True`
(PyMuPDF-tabanlı) converter'larda etkinleştirildi, LibreOffice-tabanlı
olanlar sıralı kaldı.

| # | Özellik | Neden | Sonuç |
|---|---|---|---|
| 7 | **DOCX → PDF** | `LibreOfficeEngine.convert_to()` zaten iki yönlü çalışacak şekilde genel. | ✅ `DocxToPdfConverter` eklendi — bkz. [[donusturucu-envanteri]] |
| 8 | **Çoklu görsel → tek çok-sayfalı PDF** | N girdi → 1 çıktı, mevcut 1:1 imzayı zorluyor. | ✅ `JpgToPdfConverter`, `IMergeConverter`/`MergeCapableConverter` ile genişletildi (`convert_many()`) |
| 9 | **PDF sıkıştırma/optimize** | Kullanıcılar büyük PDF'leri küçültmek ister. | ✅ `PdfCompressConverter` eklendi (PyMuPDF `deflate`/`garbage` bayrakları, rasterize etmeden) |
| 10 | **PDF birleştirme/bölme** | N:1/1:N, madde 8 ile aynı mimari ihtiyaç. | ✅ `PdfMergeConverter` (`IMergeConverter`) + `PdfSplitConverter` (mevcut 1:N modeline zaten oturuyordu) eklendi |
| 11 | **Paralel toplu dönüşüm** | LibreOffice eşzamanlılık riski. | ✅ `convert_batch_parallel()` eklendi, yalnızca `is_parallel_safe=True` converter'larda (6 PyMuPDF-tabanlı) kullanılıyor; gerçek PyMuPDF ile denendi (10 dosya, 1.37x hızlanma, veri bozulması yok) |
| 12 | **Klasör sürükle-bırak (recursive)** | Yalnızca tekil dosyalar kabul ediliyordu. | ✅ `ui/file_discovery.py` (`collect_files()`) + `DropZoneWidget` güncellendi |
| 13 | **Açık/koyu tema geçişi** | `PALETTE` merkezi tek sözlük, ikinci bir palet eklemek mantıklı. | ✅ `LIGHT_PALETTE` + `AppSettings` tema tercihi eklendi — **yeniden başlatınca uygulanır** (canlı geçiş değil, bkz. [[ui-katmani]]) |

**Yan bulgu**: N:1 çalışması sırasında `ConverterRegistry`'nin
`(source_ext, target_ext)` anahtarının aynı uzantı çiftini paylaşan
birden fazla converter'ı (üç `.pdf`→`.pdf` converter'ı: sıkıştır/böl/birleştir)
sessizce ezdiği gerçek bir bug bulundu ve düzeltildi (anahtara sınıf
adı eklendi) — bkz. [[mimari]].

## Ofis Format Genişletmesi (Word/Excel/CSV/TXT) — ✅ Tamamlandı

Kademe 1-2 bittikten sonra kullanıcı, Microsoft Office (Word/Excel) ve
PDF arasında eksik kalan yaygın dönüşümleri sordu — iki geniş matris
sunuldu (Word/PDF/TXT/RTF/ODT ve Excel/CSV/ODS/**JSON/XML**). Analiz +
kullanıcı onayıyla kapsam **Tier A**'ya daraltıldı: mevcut
`LibreOfficeEngine`/PyMuPDF'i yeniden kullanan, sıfır yeni bağımlılık
gerektiren 7 dönüşüm ailesi (9 converter) eklendi:
`PdfToTxtConverter`, `DocxToTxtConverter`, `XlsxToPdfConverter`,
`XlsxToCsvConverter`, `CsvToXlsxConverter`, `DocxToOdtConverter`,
`OdtToDocxConverter`, `XlsxToOdsConverter`, `OdsToXlsxConverter` —
detay: [[donusturucu-envanteri]].

**JSON ve XML bilinçli olarak tamamen dışında bırakıldı** — bunlar
dosya-formatı dönüşümü değil **veri-dönüştürme**: farklı bir problem
sınıfı (genel XML→tablo eşlemesi tanımsız, şemaya bağımlı). Bunları
dahil etmek "matriste bir satır daha" gibi görünüp aslında ayrı bir
ürün kapsamı (ETL aracı) açardı. RTF ailesi, HTML çıktıları, PDF→PPTX
(Tier B) de düşük değer/kalite endişesiyle bu turda alınmadı.

**Yan bulgu**: 7 converter'ın tamamen aynı `LibreOfficeEngine.convert_to()`
çağrısı dışında hiçbir mantık farkı taşımadığı görülünce
`SimpleLibreOfficeConverter` taban sınıfı çıkarıldı (bkz. [[converter-arayuzu]]) —
her biri ~8 satıra indi. Bu, "abstract kalarak `discovery.py`'den
kaçınma" deseninin ilk kullanımı; ileride benzer factory-tarzı
converter grupları için referans.

## Kademe 3 — Büyük / Stratejik (mimari zaten hazır, ayrı planlama gerekir)

| # | Özellik | Neden | Efor | Not |
|---|---|---|---|---|
| 14 | **CLI modu** | `core/conversion_facade.py` **tam olarak bunun için** Qt'siz tasarlandı (bkz. [[mimari]]) — şu an yalnızca `ui/` bunu çağırıyor. `fileconvert convert giris.pdf --hedef jpg` gibi bir komut satırı arayüzü, mimarinin doğal bir sonraki adımı. | Orta | Yeni bir `cli.py` (argparse/click) + `core.converters.discovery`/`conversion_facade` — `ui/`'a hiç dokunmadan eklenebilir, ayrım tam olarak bunu kanıtlıyor |
| 15 | **OCR desteği (taranmış PDF)** | `pdf2docx` şu an taranmış PDF'lerde "0 kelime, muhtemelen taranmış" uyarısı veriyor ve sessizce boş sonuç üretiyor (mevcut kodda zaten bu log var). Tesseract/`pytesseract` ile OCR katmanı eklenirse bu senaryo gerçek destek kazanır. | Yüksek | Yeni bir harici bağımlılık (Tesseract binary) + [[donusturucu-envanteri]]'ne yeni satır |
| 16 | **Şifreli PDF desteği** | Parola korumalı PDF'ler şu an muhtemelen sessizce/hata ile başarısız oluyor; parola sorma akışı eklenmedi. | Orta | `ConversionOptions`'a opsiyonel `password` alanı + PyMuPDF/`pdf2docx`'in şifre API'leri |
| 17 | **Harici plugin klasörü** | `core/converters/discovery.py` şu an yalnızca kendi paketini tarıyor (bkz. [[converter-ekleme]]). Kullanıcı bilgisayarındaki ayrı bir klasörü (örn. `%APPDATA%/FileConvertPro/plugins/`) de tarayacak şekilde genişletilirse gerçek 3.-parti eklenti dağıtımı mümkün olur. | Yüksek | Güvenlik notu: dış klasörden keyfi Python kodu çalıştırmak güven sınırını genişletir, imzalama/sandbox tartışılmalı |
| 18 | **Windows Gezgini sağ-tık entegrasyonu** | "Dosyaya sağ tıkla → FileConvert ile dönüştür" — masaüstü uygulaması için doğal beklenti. | Yüksek | Registry shell extension, platform-specific, paketleme (madde 5) sonrası anlamlı |
| 19 | **Çoklu dil (i18n)** | Şu an tüm UI metni Türkçe hardcoded (bkz. [[rules]] — proje dili Türkçe). Uluslararası kullanıcı hedefleniyorsa Qt `QTranslator` ile ayrıştırma gerekir. | Yüksek | Büyük bir string-çıkarma emeği; yalnızca gerçekten ihtiyaç varsa önerilir |

## Önerilen "Sonraki Versiyon" Kapsamı

Kademe 1, Kademe 2 (7 madde) ve Ofis Format Genişletmesi tamamlandı.

**Madde 14 (CLI modu) kullanıcı tarafından açıkça reddedildi** — bu
turda istenmedi, Kademe 3'ün geri kalanından (OCR, şifreli PDF, harici
plugin klasörü, sağ-tık entegrasyonu, i18n) da hiçbiri şu an gündemde
değil. İhtiyaç doğdukça ayrı ayrı değerlendirilebilir — her biri kendi
ölçeğinde bir tasarım turu gerektirir. Envanterdeki 19 converter'ın
kapsamı (bkz. [[donusturucu-envanteri]]) şu an ana odak.

## İlgili Sayfalar

- [[mimari]] — bu önerilerin oturduğu temel
- [[converter-arayuzu]] — 1:1 varsayımının kaynağı (madde 8/10 notu)
- [[converter-ekleme]] — Kademe 1/2'deki yeni converter'ların ekleneceği yer
- [[rules]] — hangi kurallara uyarak eklenecekleri
