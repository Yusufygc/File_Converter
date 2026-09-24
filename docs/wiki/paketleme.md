# Paketleme (PyInstaller)

Uygulamayı tek bir dağıtılabilir klasöre paketlemek için `fileconvert.spec`
(proje kökü) kullanılır.

## Build

```bash
pip install -r requirements-dev.txt   # pyinstaller dahil
pyinstaller fileconvert.spec
```

Çıktı: `dist/FileConvertPro/FileConvertPro.exe` (+ `_internal/` klasörü,
tüm bağımlılıkları içerir, ~130MB). `build/` ve `dist/` `.gitignore`'da
zaten hariç tutulmuş durumda.

## Neden `--onedir` (`--onefile` değil)

`.spec` dosyası `exclude_binaries=True` + `COLLECT` ile **onedir** modunu
kullanır. `--onefile` her başlatmada kendini geçici bir dizine açar; bu,
[[libreoffice-motoru]]'ndeki `subprocess` çağrıları ve MS Office
(`win32com`) COM otomasyonuyla olası geçici-dizin/izin çakışması riski
taşır. Onedir daha hızlı başlar ve bu riski taşımaz — dezavantajı yalnızca
dağıtımın "tek dosya" değil "tek klasör" olması.

## Asset Yükleme

`core/utils/resource_helper.py`'deki `get_resource_path()` zaten
`sys._MEIPASS`'i (PyInstaller'ın frozen-mode geçici kök dizini) kontrol
edecek şekilde yazılmıştı — `.spec`'teki `datas=[('assets', 'assets')]`
sayesinde ikonlar paketlenmiş exe'de de doğru bulunuyor. Bu, bu turda
gerçek bir build ile uçtan uca doğrulandı (exe başlatıldı, pencere ikonu
dahil hatasız açıldı).

## Bilinen Sınırlamalar

- **LibreOffice / Microsoft Office paketlenmiyor** — bu harici araçlar
  kullanıcının sisteminde ayrıca kurulu olmalı (bkz. [[test-ve-bagimliliklar]]).
  Paketlenmiş exe yalnızca Python/Qt/PyMuPDF/pdf2docx bağımlılıklarını içerir.
- **`.exe` simgesi mevcut** — `assets/icons/app_icon.ico` dosyası
  Windows standardındaki tüm çözünürlükleri (16x16, 24x24, 32x32, 48x48,
  64x64, 128x128, 256x256) içerir; `fileconvert.spec` ve Inno Setup
  `setup.iss` yapılandırmasında entegredir. Ayrık PNG varyantları da
  `assets/icons/` altında mevcuttur.
- Yalnızca Windows'ta test edildi (`win32com`/`pywin32` zaten yalnızca
  Windows'ta kurulu — bkz. `requirements.txt`).

## İlgili Sayfalar

- [[test-ve-bagimliliklar]] — çalışma zamanı ve harici araç bağımlılıkları
- [[libreoffice-motoru]] — onedir tercihinin gerekçesi olan subprocess mekanizması
- [[mimari]] — `resource_helper.py`'nin frozen-mode desteğinin genel mimarideki yeri
