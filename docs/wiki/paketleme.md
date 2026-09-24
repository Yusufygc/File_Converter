# Paketleme (PyInstaller)

Uygulamayı tek bir dağıtılabilir klasöre paketlemek için `fileconvert.spec`
(proje kökü) kullanılır.

## Build

```bash
pip install -r requirements-dev.txt   # pyinstaller dahil
pyinstaller fileconvert.spec
```

Çıktı: `dist/FileConvert/FileConvert.exe` (+ `_internal/` klasörü,
tüm bağımlılıkları içerir). `build/` ve `dist/` `.gitignore`'da
zaten hariç tutulmuş durumda. Exe'ye `version_info.txt` üzerinden
Windows sürüm bilgisi (şirket, ürün adı, sürüm) gömülür.

## Antivirüs Yanlış Pozitifi — PyInstaller Sürümü

`requirements-dev.txt` eskiden `pyinstaller==6.11.1`'e sabitliydi. Bu
sürümün bootloader'ı zamanla zararlı yazılımlarda da kullanıldığı için
Windows Defender imza/ML modellerine girmiş: üretilen exe derlenir
derlenmez karantinaya alınıyor, çalıştırılınca "Dosya virüslü..." hatası
veriyordu. Diğer projelerde kullanılan **6.22.3**'e yükseltilince,
exclusion olmayan bir klasörde `MpCmdRun -Scan` "found no threats"
verdi ve exe sorunsuz çalıştı. **Kural:** Defender exclusion eklemek
çözüm değildir (son kullanıcıya "güvenliği kapat" denemez) —
bootloader'ı güncel tut. Kalıcı çözüm Authenticode kod imzalamadır
(imzasız kurulumlar ilk indirmede SmartScreen "Windows bilgisayarınızı
korudu" uyarısı gösterebilir; bu antivirüs tespiti değil, itibar
kontrolüdür).

## `core/` Paketleri Normal Paket Olmalı (`__init__.py`)

Converter'lar `pkgutil` ile **dinamik** keşfedildiği için PyInstaller
onları statik analizle göremez; `.spec`'teki `collect_submodules('core')`
ile toplanırlar. `core/` ve alt klasörlerinde `__init__.py` yokken
(namespace package) `collect_submodules` alt modülleri listeleyemedi:
exe'ye yalnızca kodda doğrudan import edilen modüller girdi, kurulu
uygulamada sadece PPTX→PDF görünüyordu. Yeni bir `core/` alt klasörü
açılırsa `__init__.py` eklenmeli — `tests/test_packaging.py` bunu ve
`collect_submodules('core.converters')`'ın diskteki her modülü
bulduğunu doğrular.

## Konsol Penceresi Açılmaması (`CREATE_NO_WINDOW`)

Exe konsolsuz (`console=False`) derleniyor; buradan başlatılan konsol
programları (`tesseract.exe`, `soffice.com`) bayrak verilmezse her
çağrıda görünür bir cmd penceresi açıp kapatır. Bu yüzden
`subprocess` çağrıları `creationflags=CREATE_NO_WINDOW` kullanır
(`ocr_engine.py`, `libreoffice_engine.py`). `pytesseract.get_tesseract_version()`
bu bayrağı vermediği ve sonucu cache'lemediği için kullanılmıyor.

## Kurulum Sihirbazı (Inno Setup)

`installer/setup.iss` → `ISCC.exe setup.iss` →
`dist/installer/FileConvert_Setup_v1.0.0.exe`. Önce PyInstaller build'i
alınmış olmalı (`dist/FileConvert/`'u paketler).

- Yönetici hakkıyla **Program Files**'a kurar (`PrivilegesRequired=admin`).
- Masaüstü kısayolu görevi varsayılan olarak işaretli.
- **Tesseract OCR** isteğe bağlı görev olarak sunulur (varsayılan
  işaretsiz, ne işe yaradığı açıklamada yazılı). Seçilirse kurulum
  sonunda UB-Mannheim NSIS kurulumunu PowerShell `Invoke-WebRequest`
  ile indirip **`/S`** ile sessiz kurar (NSIS olduğu için Inno'nun
  `/VERYSILENT`'ı çalışmaz — pencere gizli açılıp kurulum asılı kalır),
  ardından `tur.traineddata`'yı `tessdata/`'ya indirir. Tesseract zaten
  kuruluysa adım atlanır; indirme/kurulum başarısız olursa kullanıcıya
  bilgi verilir ama FileConvert kurulumu iptal edilmez (OCR opsiyonel).

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
