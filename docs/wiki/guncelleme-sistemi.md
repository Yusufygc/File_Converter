# Uygulama İçi Güncelleme

Paketlenmiş uygulama açılıştan ~3 sn sonra GitHub Releases'te yeni sürüm
arar; varsa "Yeni sürüm var" penceresi çıkar. **Güncelle** → kurulum
dosyası indirilir ve doğrulanır, uygulama kapanır, kurulum sessizce
üstüne yazar, uygulama kendiliğinden yeniden açılır. Yayın tarafı:
[[surum-yayinlama]]; kurulum betiği: [[paketleme]].

## Katmanlar

| Katman | Dosya | Not |
|---|---|---|
| Servis (Qt'siz) | `core/update_service.py` | denetim, indirme, doğrulama, kurulumu başlatma, tercihler; birim testli (`tests/test_update_service.py`, ağ yok — sahte `opener`) |
| Köprü | `ui_qml/bridge/update_bridge.py` (`UpdateBridge`, QML adı `updateBridge`) | durum makinesi, arka plan iş parçacığı, Windows engelinde yeniden deneme (`tests/test_update_bridge.py`) |
| Arayüz | `ui_qml/qml/components/UpdateModal.qml` + Ayarlar → "Güncellemeler" kartı (`SettingsView.qml`) | sürüm, "Şimdi Denetle", "Açılışta yeni sürümü denetle" |
| Bağlama | `main.py` | `QTimer.singleShot(3000, startupCheck)`; `quitRequested` → `app.quit` |

Denetim yalnızca `main.py`'de tetiklenir (UI fabrikasında/testte değil:
testler ağa çıkmaz). `conftest.py` testlerde `FILECONVERT_NO_UPDATE_CHECK=1`
ve geçici `FILECONVERT_HOME` ayarlar.

## Akış

1. **Denetim:** `GET https://api.github.com/repos/Yusufygc/File_Converter/releases/latest`,
   kimlik bilgisi yok. 404 (hiç yayın yok) = "güncelsiniz". Açılış denetimi
   hatada sessiz; "Şimdi Denetle" her sonucu gösterir.
   Kapatma: Ayarlar onay kutusu ya da `FILECONVERT_NO_UPDATE_CHECK=1`.
2. **Karşılaştırma:** etiket `version.py` ile sayısal (`1.10.0 > 1.9.0`);
   taslak/ön sürüm yok sayılır; "Bu Sürümü Atla" sürümü `updates.json`'a yazar.
3. **İndirme:** `%TEMP%\FileConvertUpdate`, ilerleme çubuğu, doğrulamalar (aşağıda).
4. **Kurulum:** `FileConvert-Setup-X.Y.Z.exe /SILENT /SUPPRESSMSGBOXES /CLOSEAPPLICATIONS
   /CURRENTUSER|/ALLUSERS /LOG=...\install.log`, bağımsız süreç, kabuk yok. Kurulum modu
   ÇALIŞAN exe'nin yerinden çıkarılır (`install_mode_arguments`): `%LOCALAPPDATA%`
   altındaysa `/CURRENTUSER`, değilse `/ALLUSERS`. Inno'da
   `PrivilegesRequiredOverridesAllowed=commandline dialog` bunun için şart. Uygulama 1.5 sn sonra kapanır; Inno `[Run]
   Check: RelaunchAfterUpdate` ile yeniden açar.
5. **Windows engellerse:** `CreateProcess` → `WinError 4551/1260` →
   Gezgin yolu (`ShellExecuteW`) → yine engelse 15 sn aralıkla en çok
   40 deneme ("Windows bekleniyor…", "Beklemeyi Bırak"); bırakılırsa dosya
   Gezgin'de seçili gösterilir + "Sürüm Sayfası".

## Güvenlik (kaldırılmaz)

- İndirme adresi yalnızca `https://github.com/Yusufygc/File_Converter/releases/download/...`;
  yönlendirme yalnızca `github.com` / `*.githubusercontent.com`.
- Dosya adı sıkı desen `^FileConvert-Setup-\d+\.\d+\.\d+\.exe$` (indirme ve başlatma).
- Boyut ≤ 400 MB ve Release'teki boyutla birebir; yanıt boyutu/süresi sınırlı.
- **SHA-256 zorunlu:** asset `digest` alanı, yoksa Release'teki `.sha256`;
  ikisi de yoksa güncelleme reddedilir; uyuşmazlıkta dosya silinir.
- Sürüm notları düz metin gösterilir.
- Kullanıcıya giden mesajlar teknik terimsiz ([[hata-yonetimi]]); ayrıntı günlüğe.
- **Sınır:** özet GitHub'dan gelir; hesap ele geçirilirse sahte dosya +
  sahte özet yayınlanabilir (imzasız dağıtımın doğası).

## Tercihler

`%LOCALAPPDATA%\FileConvert\updates.json` (`check_on_startup`,
`skipped_version`); bozuksa varsayılanlar. Kök `core/utils/app_paths.py`
(`FILECONVERT_HOME` ile değiştirilebilir).

## Gerçek Deneme (2026-11-13, bu makine, v1.1.1 → v1.1.2)

Release'ten indirilen 1.1.1 kullanıcı kurulumu açıldı → ~3 sn sonra "Yeni
sürüm var" penceresi → Güncelle → indirme + SHA-256 (GitHub `digest`) →
sessiz kurulum ("Installation process succeeded") → uygulama 1.1.2 olarak
kendiliğinden açıldı (günlük: "FileConvert 1.1.2 başlatılıyor"). CI'da
derlenen 1.1.1 ve 1.1.2 kurulumlarındaki exe özeti yerelle aynı
(`559c5fe5…`): kararlı exe sahada doğrulandı.

**Bulgu (düzeltildi):** makinede aynı AppId'li eski 1.0.0 yönetici kurulumu
(Program Files, HKLM) da vardı. Inno önceki yönetici modunu seçip
(`UsePreviousPrivileges` varsayılanı, günlük: "Administrative install mode: Yes")
kullanıcı kurulumunu değil **eski yönetici kurulumunu** 1.1.2'ye yükseltti.
Düzeltme: güncelleyici kurulum modunu çalışan exe'nin yerine göre zorlar
(yukarıda, adım 4); Inno komut satırı geçersiz kılmasına izin verir. Düzeltme
güncellemeyi BAŞLATAN sürümde olmalı: 1.1.3 ve sonrasından güncellenen
kurulumlarda etkili; 1.1.1/1.1.2'den güncelleme yine eski davranışı gösterebilir
(yalnızca hem eski yönetici hem kullanıcı kurulumu olan makinelerde).

## Sınırlar / Doğrulanmayanlar

- `/CURRENTUSER` düzeltmesinin gerçek bir güncellemede denenmesi (1.1.3 → 1.1.4)
  **doğrulanmadı**; birim testi ve Inno derlemesi var. Sorun olursa
  `%TEMP%\FileConvertUpdate\install.log` ("Administrative install mode" satırı).
- 1.0.0 kurulumlarında güncelleyici yok: 1.0.0 kullanıcıları 1.1.0'ı bir kez
  elle kurar (kurulum eski yönetici kurulumunu kaldırmayı teklif eder).
- Yalnızca Windows. İndirme sürerken iptal yok.

## İlgili Sayfalar

- [[surum-yayinlama]] — yayın adımları
- [[paketleme]] — Inno `RelaunchAfterUpdate`, kararlı exe
- [[hata-yonetimi]] — mesaj ve günlük kuralları
- [[ui-katmani]] — köprü/QML deseni
