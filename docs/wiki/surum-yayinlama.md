# Sürüm Yayınlama

Yeni sürüm **etiket** ile yayınlanır: `vX.Y.Z` etiketi push edilince
`.github/workflows/release.yml` testleri koşar, kararlı exe'yi ve Inno
kurulum dosyasını derler, GitHub Releases'e yükler. Kurulu uygulamalar
açılışta bu yayını görüp güncelleme teklif eder ([[guncelleme-sistemi]]).
Exe ve kurulum ayrıntıları: [[paketleme]].

## Sürüm Numarası

- Biçim `MAJOR.MINOR.PATCH`, etiket `v` önekli (`v1.1.0`). Ön sürüm
  (`v1.2.0-rc1`) Release'te ön sürüm olur, güncelleyici yok sayar.
- **Tek kaynak:** kökteki `version.py` (`__version__`, `APP_NAME`,
  `RELEASE_REPO = "Yusufygc/File_Converter"`). README rozeti
  `tools/release.py` ile aynı değere çekilir; elle düzenlenmez (test denetler).
- Exe'nin Windows sürüm kaynağı **bilerek** hep `1.0.0.0` ([[paketleme]]).
- Artış: hata düzeltme → PATCH, özellik → MINOR, uyumsuz değişiklik → MAJOR.
- Başlangıç: 1.0.0 elle dağıtılmıştı (yönetici kurulumu, Release yok);
  sürüm sistemi **1.1.0** ile başlar (kullanıcı kararı, 2026-11-13).

## Adımlar

Ön koşul: `python -m pytest tests/ -q` yeşil, çalışma ağacı temiz, dal `main`.

```powershell
python tools/release.py 1.1.0   # version.py + README rozeti -> "chore(release): v1.1.0" commit'i -> v1.1.0 etiketi (itmez)
git push origin main
git push origin v1.1.0          # --follow-tags KULLANMA: ek açıklamasız etiketleri göndermez
gh run watch
gh release view v1.1.0          # kurulum dosyası ve .sha256 var mı
```

`tools/release.py` koşulları: dal `main`, ağaç temiz, yeni sürüm mevcuttan
büyük, etiket yok. **Hiçbir şey göndermez.** Not: `version.py` zaten 1.1.0
olduğu için ilk yayın `tools/release.py` olmadan, doğrudan
`git tag -a v1.1.0 -m "FileConvert 1.1.0"` ile etiketlenebilir; sonraki
sürümler (1.1.1, 1.2.0...) araçla.

Release iş akışı sırası:
1. `tools/release.py --check-tag "$env:TAG"` — etiket ≠ `version.py` ise durur.
   Etiket adı `env: TAG` ile verilir (betiğe gömülmez: komut enjeksiyonu yok).
2. Bağımlılıklar `-c requirements-lock.txt` ile (geçişli sürümler sabit), `pytest`.
3. Inno Setup yoksa `choco install innosetup`.
4. `python build_installer.py` — **kararlı exe kapısı**: özet
   `packaging/launcher.sha256` ile aynı değilse yayın durur.
5. `gh release create ... --generate-notes --verify-tag` (notlar commit
   mesajlarından: commit mesajları anlaşılır yazılır).

`test.yml` (her push, Ubuntu) ayrı iş akışıdır; yayın ona bağlı değildir.

## Yayından Sonra

- CI günlüğünde "Kararlı exe özeti onaylananla aynı" satırını gör. Görmezsen
  ve iş akışı durduysa: CI exe'si yerelden farklıdır (Python/PyInstaller/
  kilit dosyası/satır sonu farkı) — [[paketleme]] "Exe'yi bilerek değiştirmek".
- Release'teki kurulum dosyasını **indirip** (MOTW'li) bu makinede aç:
  CI'da derlenen dosya yerelde denenmemiş dosyadır.
- Önceki sürümden uygulama içi güncellemeyi dene (pencere çıktı mı, kurulum
  başladı mı, uygulama kendiliğinden açıldı mı, Ayarlar'da yeni sürüm mü).

## Hata ve Geri Alma

| Durum | Yapılacak |
|---|---|
| Etiket ≠ sürüm, iş akışı durdu (yayın yok) | Düzelt, commit'le, etiketi taşı: `git tag -f vX.Y.Z`, `git push -f origin vX.Y.Z` |
| Derleme adımı düştü (yayın yok) | Sebebi düzelt, etiketi aynı yolla taşı |
| Yayın oluştu ama hatalı | **Yayınlanmış etiketi taşıma.** Yeni PATCH çıkar. Acilse `gh release delete vX.Y.Z --cleanup-tag` |
| Kapı "özet DEĞİŞTİ" | [[paketleme]] "Exe'yi bilerek değiştirmek" |
| Kullanıcıda güncelleme başlamadı | `%TEMP%\FileConvertUpdate\install.log` |

## Kurallar

- **Etiket oluşturma ve etiket push'u yalnızca kullanıcının açık isteğiyle**
  (yapay zekâ ajanları dahil): etiket itmek tüm kurulu kullanıcılara
  güncelleme penceresi çıkarır. Bkz. [[rules]].
- Kurulum dosyası imzasız (karar): SmartScreen "Ek bilgi → Yine de çalıştır";
  SAC engelinde bu seçenek yok, birkaç dakika sonra yeniden çalıştırılır (README'de).
- İndirme/doğrulama kuralları kaldırılmaz ([[guncelleme-sistemi]]).

## İlgili Sayfalar

- [[paketleme]] — kararlı exe, kapı, Inno, deneme
- [[guncelleme-sistemi]] — kullanıcı tarafı
- [[test-ve-bagimliliklar]] — CI ve bağımlılık dosyaları
