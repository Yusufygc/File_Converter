# Kronolojik Kayıt

En yeni girişler en üstte. Format: `[YYYY-AA-GG] [İŞLEM_TİPİ] | Açıklama`
İşlem tipleri: `INGEST` (yeni özellik/kaynak), `REFACTOR` (mimari
değişiklik), `FIX` (hata düzeltme), `DOCS` (dokümantasyon).

## [2026-09-12] [INGEST] | Kademe 2 güvenli 4 madde tamamlandı

Yol haritasındaki (bkz. [[yol-haritasi]]) 7 Kademe 2 maddesinden N:1
mimari genişlemesi gerektiren (8, 10) ve LibreOffice eşzamanlılık
riski taşıyan (11) kullanıcı kararıyla ertelendi; güvenli 4 madde
uygulandı: `DocxToPdfConverter`, `PdfCompressConverter` (üzerine yazma
korumalı `get_output_path()` override'ı ile), `ui/file_discovery.py`
(klasör sürükle-bırak, alt klasörler dahil), açık/koyu tema
(`LIGHT_PALETTE` + `AppSettings` tema tercihi, yeniden başlatınca
uygulanır — canlı geçiş değil). Test sayısı 18'den 31'e çıktı. Detay:
[[donusturucu-envanteri]], [[ui-katmani]], [[test-ve-bagimliliklar]].

## [2026-09-12] [INGEST] | Kademe 1 tamamlandı

Yol haritasındaki (bkz. [[yol-haritasi]]) 6 hızlı-kazanım maddesi
uygulandı: iptal butonu (tek buton toggle), `PdfToPngConverter`,
dosya türü ikonları (`ui/icon_map.py`), `AppSettings` (QSettings ile
pencere/converter/seçenek kalıcılığı), `.github/workflows/test.yml`
(CI), `fileconvert.spec` (PyInstaller — gerçek bir build ile
`dist/FileConvertPro/FileConvertPro.exe` üretilip başlatılarak
doğrulandı). Test sayısı 14'ten 18'e çıktı. Detay: [[ui-katmani]],
[[donusturucu-envanteri]], [[paketleme]], [[test-ve-bagimliliklar]].

## [2026-09-12] [DOCS] | Yol haritası raporu eklendi

Yeni versiyon için kademeli (hızlı kazanım / orta vadeli / stratejik)
özellik önerileri raporu yazıldı — bkz. [[yol-haritasi]].

## [2026-09-12] [DOCS] | Wiki mekanizması kuruldu

`docs/wiki/` altında bu bilgi tabanı ve proje kökünde `CLAUDE.md`
oluşturuldu — bkz. [[index]].

## [2026-09-12] [REFACTOR] | Backend/frontend ayrımı ve tak-çıkar mimari

`core/` katmanı Qt bağımlılığından tamamen ayrıldı
(`core/conversion_facade.py`, `ui/adapters/qt_conversion_runner.py`).
`BaseConverter` template method ile her converter'daki tekrar eden kod
(~15-20 satır × 5 dosya) tek yere toplandı. `core/converters/discovery.py`
ile otomatik converter keşfi eklendi — `CONV_*` sabitleri, `conv_map`,
hardcoded dropdown `addItem()` çağrıları kaldırıldı. `IEngineSelectable`
opsiyonel capability protokolü ile motor-seçimi UI mantığı belirli bir
dönüşüm türünü hardcode etmekten kurtarıldı. Paylaşılan
`LibreOfficeEngine` ile PPTX/PDF-DOCX'teki ~60 satırlık kod tekrarı
giderildi. `core/` için Qt gerektirmeyen 14 pytest testi eklendi
(`tests/`). Detay: [[mimari]], [[converter-arayuzu]], [[rules]].

## [2026-09-12] [INGEST] | PDF→JPG ve JPG→PDF dönüştürücüleri eklendi

PyMuPDF (`fitz`) ile `PdfToJpgConverter` (çok sayfalı PDF'te her sayfa
ayrı JPG) ve `JpgToPdfConverter` (`.jpg`+`.jpeg` kabul eden, tek sayfalı
PDF üreten) eklendi. Options panel'e JPEG kalite ayarı, özet dialoguna
sayfa sayısı gösterimi eklendi. Detay: [[donusturucu-envanteri]].

## [2026-03-17] [INGEST] | Dosya listesi hover/solukluk düzeltmeleri

Yüklenen dosyaların isim ve boyut etiketlerindeki solukluk giderildi,
hover rengi dengelendi.

## [2026-03-17] [INGEST] | UI düzenlemesi yapıldı

Genel arayüz düzenlemesi (tema, layout).

## [2026-03-17] [INGEST] | Klasör yapısı ve temel kod iskeleti oluşturuldu

Proje temel dizin yapısı (`core/`, `ui/`, `services/`) ve ilk
`PptxToPdfConverter` implementasyonu oluşturuldu.
