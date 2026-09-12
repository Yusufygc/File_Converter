# FileConvert Pro — Proje Talimatları

PySide6 ile yazılmış masaüstü dosya dönüştürücü uygulaması (PPTX/PDF/JPG
arası dönüşümler). Backend (`core/`) ve frontend (`ui/`) fiziksel olarak
ayrılmıştır; `core/` hiçbir zaman Qt import etmez.

## Önce Oku (No Zero-Context)

Kod yazmadan, mimari bir karar vermeden veya bu proje hakkında bir soruyu
yanıtlamadan önce **mutlaka `docs/wiki/index.md` dosyasını oku**. İhtiyaç
duyarsan oradaki `[[sayfa]]` bağlantılarını takip ederek alt sayfaları
incele. Projeyi kaynak koddan sıfırdan keşfetmek yerine biriken bilgiyi
kullan; `docs/wiki/rules.md` bu projenin kodlama ve commit kurallarının
tek kaynağıdır.

## Proaktif Güncelleme (Bookkeeping)

Konuşma sırasında yeni bir kütüphane eklenirse, bir mimari karar alınırsa
veya karmaşık bir mekanizma tasarlanırsa, bunu yalnızca sohbet bağlamında
tutma — arka planda ilgili `docs/wiki/` sayfasını güncelle veya yenisini
aç, `docs/wiki/index.md`'ye linkle, `docs/wiki/log.md`'ye kronolojik
kaydını düş (en yeni giriş en üstte, format için `log.md`'nin başına bak).
Oluşturduğun her sayfada Obsidian tarzı `[[cift_koseli_parantez]]` ile
ilgili diğer sayfalara atıfta bulun — öksüz (hiçbir yere bağlanmayan)
sayfa bırakma.

## Operasyon Komutları

- **İNGEST** — yeni bir özellik/kaynak/karar geldiğinde: ilgili
  `docs/wiki/` sayfasını oluştur/güncelle, `index.md`'ye linkle,
  `log.md`'ye `[İNGEST]` girişi ekle.
- **QUERY** — proje hakkında detaylı bir soru geldiğinde: önce
  `docs/wiki/index.md` üzerinden ilgili sayfaları bul ve oku, yalnızca
  genel bilgiyle cevap verme; sonuç kalıcı bir mimari kararsa wikiye ekle.
- **LINT** — "wiki'yi lint et" istendiğinde: `docs/wiki/` içindeki tüm
  sayfaları tara, çelişen/güncelliğini yitirmiş bilgi, öksüz sayfa veya
  kırık `[[link]]` var mı kontrol et, rapor sun, onay sonrası düzelt.

## Hızlı Komutlar

```bash
python main.py                    # uygulamayı çalıştır
python -m pytest tests/ -v        # testleri çalıştır (Qt gerektirmez, ~0.5s)
pip install -r requirements.txt        # çalışma zamanı bağımlılıkları
pip install -r requirements-dev.txt    # + pytest
```

## Kurallar

Kodlama stili, mimari invariantlar (`core/` Qt'siz kalır, yeni converter
`core/converters/`'a tek dosya eklenerek tanımlanır) ve commit kuralları
için: `docs/wiki/rules.md`. Bu dosyada tekrar edilmez, oradan okunur.
