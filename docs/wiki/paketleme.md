# Paketleme (PyInstaller + Inno Setup)

Exe ve kurulum dosyası tek komutla üretilir; exe **her sürümde bayt bayt
aynıdır** ("kararlı exe"). Yayın adımları: [[surum-yayinlama]].
Uygulama içi güncelleme: [[guncelleme-sistemi]].

Kaynak rehber (proje dışı, genel şablon):
`C:\2UYGULAMALAR\D002-HazirPromptlar\Prod hazırlığı\exe-dagitim-rehberi.md`.
Bu sayfa o rehberin bu projedeki uygulamasıdır; gerekçelerin ayrıntısı orada.

## Komutlar

```bash
pip install -r requirements-dev.txt -r requirements-build.txt -c requirements-lock.txt
python build_installer.py                         # exe + kapı + deneme + Inno + .sha256 + kurulum denemesi
python build_installer.py --no-verify             # bu makinede deneme yapmadan
python build_installer.py --skip-build            # mevcut dist/ ile yalnızca Inno
python build_installer.py --update-launcher-hash  # exe'yi BİLEREK değiştirdiysen (aşağıya bak)
python build_exe.py                               # yalnızca exe (kapı dahil)
```

Çıktılar: `dist/FileConvert/FileConvert.exe` (+ `_internal/`),
`dist/installer/FileConvert-Setup-X.Y.Z.exe` ve `.sha256`.
Eski `fileconvert.spec`, kökteki `version_info.txt` ve `installer/setup.iss`
kaldırıldı; yerlerini `build_exe.py` ve `packaging/` aldı.

## Neden Kararlı Exe

Windows 11 Akıllı Uygulama Denetimi (SAC) **imzasız** her exe'yi dosya
özetine (SHA-256) göre bulut itibarına bırakır; karar öngörülemez.
Her sürümde yeni exe = her güncellemede yeni engel riski (kurulum başarılı
görünür ama uygulama açılmaz). Çözüm: exe'yi sürümler arasında
değiştirmemek; sürümle değişen kod exe dışında `.pyc` olarak durur.
Kod imzalama yapılmıyor (karar).

Dört parça (biri eksikse özet değişir):

| Parça | Dosya / ayar |
|---|---|
| Sabit giriş betiği | `packaging/launcher.py` — yalnızca `main.main()` çağırır. **Asla değiştirilmez** (docstring dahil exe'ye girer) |
| Modüller exe dışında | `--debug=noarchive` (uygulama kodu `_internal/**.pyc`) |
| Sabit zaman damgası | `SOURCE_DATE_EPOCH = LAUNCHER_EPOCH = 1700000000` (`build_exe.py`) |
| Sabit sürüm kaynağı | `packaging/launcher_version_info.txt`, hep `1.0.0.0` (Gezgin → Özellikler hep 1.0.0.0 gösterir; ürün sürümü kurulumda, "Uygulamalar ve özellikler"de ve Ayarlar'da) |

Ayrıca sabit: `pyinstaller==6.22.3` (`requirements-build.txt`), Python 3.10
(yerel = CI), geçişli sürümler `requirements-lock.txt`, satır sonları
`.gitattributes` (`* text=auto eol=lf`).

### Onay kapısı: `packaging/launcher.sha256`

Bu makinede **açılarak denenmiş** exe özeti depodadır. `build_exe.py`
derlemeden sonra karşılaştırır; farklıysa ya da dosya yoksa derleme ve
yayın **durur**. CI aynı kapıdan geçer.

Ölçüm (2026-11-13, bu makine, Windows 11, Python 3.10.11, PyInstaller 6.22.3):

| Deney | Sonuç |
|---|---|
| 3 ayrı derleme, arada uygulama kodu (`app_bridge.py`) değişti | özet hep `559c5fe5…09bd` |
| `launch_check` (10 sn, izole `FILECONVERT_HOME`) | hatasız çalıştı; günlük: "32 dönüştürücü yüklendi; kullanılamayan: yok" |
| `installer_check` (sessiz kurulum → exe → kaldırıcı) | başarılı; gerçek 1.0.0 kaydı (HKLM) ve kısayollar bozulmadı |
| Kurulum dosyası boyutu | 94 MB (`dist/FileConvert` 370 MB) |
| CI'da derlenen exe'nin özeti yerelle aynı mı | **aynı** (v1.1.1 ve v1.1.2 Release'leri, `windows-latest`) |
| İndirilmiş (MOTW'li) kurulum dosyası başka/SAC'lı makinede | **doğrulanmadı** |

### Deneme kapısının açığı (yaşandı)

İlk derlemede `launch_check` "8 sn çalıştı → başarılı" dedi; oysa uygulama
açılışta yakalanmamış hata verip **hata penceresiyle açık kalmıştı**
(`pymupdf4llm` düzen modelinin veri dosyaları pakete girmemişti). Artık
`build_verify.launch_check` denemenin izole günlüğünde `CRITICAL` /
"Yakalanmamış hata" arar; varsa başarısız sayar. Ders: "süreç çalışıyor"
tek başına başarı kanıtı değildir.

## Exe'yi BİLEREK Değiştirmek (nadir)

Gerekçeler: PyInstaller/Python sürümü, simge, `launcher.py`, sürüm kaynağı,
**PyInstaller bağımsız değişkenleri** (`--exclude-module`, `--collect-*`
eklemek özeti değiştirdi — ölçüldü). Sıra:

1. `python build_exe.py` (kapı durur ama exe `dist/` altında oluşur).
2. Bu makinede aç: `python -c "import build_exe, build_verify; print(build_verify.launch_check(build_exe.executable_path()))"`.
3. Engellenirse **yalnızca** `LAUNCHER_EPOCH`'u değiştir, yeniden derle, tekrar dene
   (aynı epoch ile yeniden derlemek aynı exe'yi verir; "şansa derleme" döngüsü yok).
4. Açılınca onayla: `python build_installer.py --update-launcher-hash`.
5. `launcher.py`/sürüm kaynağı değiştiyse `tests/test_release_packaging.py` sabit özetlerini güncelle.
6. Commit'le. Bu tüm kullanıcılar için **yeni** exe demektir; sık yapma.

Boyut küçültmek için Qt parçalarını **derleme sonrası silmek** (`prune`,
`UNUSED_QML_DIRS`/`UNUSED_DLL_PREFIXES`) özeti etkilemez (silinenler exe dışında).

## Paket İçeriği Kararları

- **Dinamik keşif:** converter'lar `pkgutil` ile bulunur; `--collect-submodules=core`
  (ve `ui_qml`, `pdf2docx`, `pymupdf4llm`, `openpyxl`, `tabulate`) ile açıkça
  toplanır. `core/` altındaki her klasörde `__init__.py` olmalı (yoksa
  namespace package olur ve `collect_submodules` alt modülleri bulamaz —
  1.0.0'da kurulu uygulamada yalnızca PPTX→PDF görünmüştü);
  `tests/test_packaging.py` bunu denetler.
- **PDF→Markdown düzen modeli pakette yok:** `pymupdf4llm` import edilince
  `pymupdf.layout` (ONNX) modelini kendiliğinden açıyordu; model
  onnxruntime + sympy + networkx ile ~60 MB ekliyor, veri dosyaları
  PyInstaller'a girmediği için exe açılışta çöküyordu. `--exclude-module`
  ile çıkarıldı, kod `sys.modules["pymupdf.layout"] = None` ile klasik moda
  zorluyor (geliştirme ortamı = exe). Bkz. [[donusturucu-envanteri]].
- **`--onedir`:** `--onefile` her açılışta `%TEMP%`'e açılır; LibreOffice/COM
  süreçleriyle çakışma riski ve yavaş açılış. Inno ile birlikte tek kurulum dosyası.
- **`--noupx`:** UPX DLL imzalarını bozar, antivirüs yanlış pozitifini artırır.
- **Konsol penceresi:** exe `--windowed`; başlatılan konsol programları
  (`tesseract.exe`, `soffice.com`) `creationflags=CREATE_NO_WINDOW` kullanır.
- **Antivirüs:** `pyinstaller==6.11.1` bootloader'ı Defender'a takılıyordu;
  6.22.3 temiz. Defender istisnası eklemek çözüm değildir.
- **Asset'ler:** `--add-data` ile `assets/` ve `ui_qml/qml/`; `get_resource_path()`
  `sys._MEIPASS`'i (`_internal`) kullanır.

## Kurulum Sihirbazı (`packaging/FileConvert.iss`)

Sürüm `build_installer.py`'den `/DAppVersion` ile gelir (elle derlenirse
`#error`). UTF-8 BOM'lu (Türkçe metinler).

- `AppId={{8E478C22-…}` **sabit** (1.0.0 ile aynı): değişirse ikinci kurulum olur.
- `PrivilegesRequired=lowest` (+ `OverridesAllowed=commandline dialog`; `commandline`,
  güncelleyicinin `/CURRENTUSER`/`/ALLUSERS` geçebilmesi için — bkz. [[guncelleme-sistemi]]): UAC sormaz,
  `%LOCALAPPDATA%\Programs\FileConvert`'e kurar; uygulama içi sessiz
  güncelleme bunun için şart (admin kurulum Python'dan başlatılınca 740 verir).
- `CloseApplications=yes`, `RestartApplications=no`; yeniden açma `[Run]`
  satırındaki `Check: RelaunchAfterUpdate` ile: `/SILENT` (güncelleme)
  yeniden açar, `/VERYSILENT` (derleme sonrası deneme) açmaz.
- Çıktı adı `FileConvert-Setup-X.Y.Z.exe` (güncelleyici bu desene bakar).
- **1.0.0 geçişi:** 1.0.0 yönetici olarak Program Files'a kuruluyordu (HKLM).
  Kullanıcı-başına kurulumda eski HKLM kaydı bulunursa (sessiz modda değil)
  "eski sürüm kaldırılsın mı?" sorulur, evetse eski kaldırıcı UAC ile
  çalıştırılır. **Doğrulanmadı** (etkileşimli; yalnızca derlendi).
- **Tesseract (isteğe bağlı görev):** Program Files'a kurulduğu için yönetici
  ister. İndirmeler yetkisiz yapılır; NSIS kurulumu (`/S`) + `tur.traineddata`
  kopyalama **tek** yükseltilmiş PowerShell sürecinde (`ShellExec('runas')`)
  → tek UAC onayı. Sessiz kurulumda (güncelleme; Inno önceki görev
  seçimlerini hatırlar) bu adım atlanır, güncellemede UAC çıkmaz.
  **Doğrulanmadı** (etkileşimli UAC; yalnızca derlendi).
- Kullanıcı verisi (`%LOCALAPPDATA%\FileConvert`) kaldırıcıyla silinmez.

## Derleme Sonrası Deneme (`build_verify.py`)

- `launch_check`: exe'yi `FILECONVERT_HOME=<geçici>` +
  `FILECONVERT_NO_UPDATE_CHECK=1` ile açar (ayarlar INI'ye gider, kayıt
  defterine/gerçek günlüğe dokunmaz, ağ isteği yok), süre sonunda kapatır,
  günlükte ölümcül hata arar. `WinError 4551/1260` = SAC engeli.
- `installer_check`: geçici klasöre `/VERYSILENT /CURRENTUSER` kurar, exe'yi
  açar, kaldırıcıyı da çalıştırır. Deneme gerçek kurulumla aynı `AppId`'yi
  kullandığı için HKCU Uninstall kaydı ve Başlat menüsü kısayolları önce
  yedeklenir, `try/finally` ile her durumda geri yazılır.
- CI'da (`CI` ortam değişkeni) deneme atlanır: CI Windows'unda SAC yoktur.

## YAPILMAMASI Gerekenler

- Her sürümde yeni exe özeti üretmek; engellenince "şansa yeniden derlemek".
- `launcher.py` / `launcher_version_info.txt`'ye dokunmak, onaydan sonra
  PyInstaller bağımsız değişkeni eklemek (bilerek değilse).
- Kapıyı atlamak (`--no-verify` ile yayın, özet dosyasını CI'da üretmek).
- Inno kurulum dosyasını "açılıyor mu" diye elle başlatıp öldürmek
  (deneme yalnızca sessiz, geçici klasöre, kaldırıcıyla).
- UPX, SAC'ı kapatmayı önermek, Defender istisnası.

## İlgili Sayfalar

- [[surum-yayinlama]] — etiket, `tools/release.py`, Release iş akışı
- [[guncelleme-sistemi]] — uygulama içi güncelleme ve güvenlik kuralları
- [[test-ve-bagimliliklar]] — bağımlılık dosyaları ve CI
- [[hata-yonetimi]] — günlük dosyası (deneme kapısı onu okur)
- [[libreoffice-motoru]] — onedir tercihinin gerekçesi olan subprocess mekanizması
- [[mimari]] — `resource_helper.py`'nin frozen-mode desteği
