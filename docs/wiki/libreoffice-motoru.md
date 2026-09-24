# LibreOffice Motoru

`core/converters/libreoffice_engine.py` → `LibreOfficeEngine` sınıfı.
Önceden `pptx_to_pdf.py` ve `pdf_to_docx.py` içinde birebir kopyalanmış
~60 satırlık tespit + subprocess mantığının ortaklandığı yer.

## Ne Yapar

```python
class LibreOfficeEngine:
    def is_available(self) -> bool: ...
    def convert_to(self, source_path, output_path, target_ext, extra_args=None) -> None: ...
```

- `_detect()`: `libreoffice`/`soffice`'i PATH'te (`shutil.which`) veya
  bilinen kurulum yollarında (`C:\Program Files\LibreOffice\...`, macOS/Linux
  yolları) arar.
- `convert_to()`: `soffice --headless --invisible --nologo --norestore
  -env:UserInstallation=<profil> --convert-to <ext> --outdir <dir> <source>`
  çalıştırır (`CREATE_NO_WINDOW` ile), çıktının beklenen yerde olduğunu
  doğrular (yoksa kaynak dizine fallback bakar), gerekiyorsa istenen
  `output_path`'e taşır.

## İzole Profil (`-env:UserInstallation`)

Uygulama kendi kalıcı profilini kullanır:
`%LOCALAPPDATA%\FileConvert\libreoffice_profile`. LibreOffice tek örnekli
çalışır; varsayılan profil paylaşılırsa kullanıcının **açık LibreOffice
penceresi** dönüşüm isteklerini devralır. O pencere meşgulken (ör. büyük
bir belge yüklüyorken) dönüşüm boş bir `"LibreOffice hatası:"` ile başarısız
oldu (bu oturumda gerçekten yaşandı). İzole profille dönüşüm başına ~0.9–1.6
sn soğuk başlatma maliyeti var; profil kalıcı olduğu için ~3 sn'lik profil
oluşturma yalnızca ilk kez ödenir.

Denenip elenen: uygulamanın kendi arka plan LibreOffice örneğini sıcak
tutup `--convert-to` isteklerini ona devretmek. Headless örnek devredilen
ilk isteği işledikten sonra kendini kapatıyor; güvenilir değil (kalıcı
sıcak örnek için UNO API gerekir, LibreOffice'in kendi Python'uyla — paketleme
maliyeti yüksek).

## `writer_pdf_import` Neden Artık Kullanılmıyor

PDF'i LibreOffice'e doğrudan açtırmak (`--infilter=writer_pdf_import`,
yoksa `"no export filter"` hatası) çizim yoğun PDF'lerde patolojik derecede
yavaş: 45 sayfalık vektör ağırlıklı bir ders notunda 15 dk zaman aşımına
takıldı. Üstelik her satırı ayrı konumlandırılmış metin kutusu yapıyor
(17 sayfalık makalede 2181 metin kutusu) — çıktı düzenlenemez.
`PdfToOdtConverter` artık PDF'i `PdfToDocxConverter` hattıyla (pdf2docx /
OCR / görsel gömme) geçici DOCX'e çevirip LibreOffice'e yalnızca DOCX→ODT
yaptırıyor (aynı PDF'ler: 40 sn, 0 metin kutusu, 1172 paragraf). Filtre
yalnızca `PdfToDocxConverter`'ın pdf2docx kurulu değilken kullandığı son
çare yolda duruyor.

## Kimler Kullanıyor

- `PptxToPdfConverter._LibreOfficeStrategy` — MS Office yoksa fallback
- `PdfToDocxConverter._LibreOfficePdfStrategy` — pdf2docx yoksa fallback
- `PdfToOdtConverter` — ara DOCX'i ODT'ye çevirmek için
- `office_conversions.py`'deki `SimpleLibreOfficeConverter` alt sınıfları

## Alternatif Motorlar (LibreOffice'e ihtiyaç duymayanlar)

- **MS Office (win32com)**: yalnızca Windows + Office kurulu + `pywin32`.
  PPTX→PDF'te tercih edilir (daha hızlı, LibreOffice kurulumu gerektirmez).
- **pdf2docx**: saf Python, PDF→DOCX'te tercih edilir.
- **PyMuPDF (fitz)**: PDF→JPG ve JPG→PDF'te LibreOffice'e hiç ihtiyaç
  duymaz — bkz. [[donusturucu-envanteri]].

## İlgili Sayfalar

- [[donusturucu-envanteri]] — hangi converter'ın hangi motoru kullandığı
- [[converter-ekleme]] — yeni bir LibreOffice-tabanlı converter eklerken bu sınıfı yeniden kullanma
