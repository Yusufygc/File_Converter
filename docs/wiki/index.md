# FileConvert Pro — Wiki İndeksi

PySide6 tabanlı masaüstü dosya dönüştürücü uygulamasının bilgi tabanı.
Kod yazmadan veya mimari bir karar vermeden önce bu sayfa okunur —
bkz. proje kökündeki `CLAUDE.md`.

## Mimari

- [[mimari]] — backend/frontend fiziksel ayrımı, katman diyagramı, veri akışı
- [[converter-arayuzu]] — `IConverter`, `BaseConverter`, `IEngineSelectable` sözleşmeleri

## Converter Sistemi

- [[converter-ekleme]] — yeni dönüşüm türü ekleme rehberi (tak-çıkar mimari)
- [[donusturucu-envanteri]] — mevcut converter'ların tablosu (motor, davranış)
- [[libreoffice-motoru]] — paylaşılan `LibreOfficeEngine`, `--infilter` gerekliliği

## UI Katmanı

- [[ui-katmani]] — `MainWindow`, widget'lar, `QtConversionRunner`, `converter_catalog`, `AppSettings`

## Test & Bağımlılıklar

- [[test-ve-bagimliliklar]] — `tests/` yapısı, `requirements*.txt`, harici araçlar, CI
- [[paketleme]] — PyInstaller ile dağıtılabilir exe üretme

## Kurallar

- [[rules]] — kodlama kuralları, commit kuralları, bilinçli kapsam-dışı kararlar

## Yol Haritası

- [[yol-haritasi]] — yeni versiyon için kademeli özellik/geliştirme önerileri

---

Kronolojik değişiklik kaydı için: [[log]]
