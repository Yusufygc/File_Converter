# Kurallar

Bu proje üzerinde çalışırken (insan veya LLM fark etmez) uyulması
beklenen kodlama ve commit kuralları. Mevcut kod tabanından ve bu
projede gözlemlenen tercihlerden türetilmiştir — icat değildir.

## Dil

- Docstring, kod içi yorum ve commit mesajları **Türkçe** yazılır.
- Değişken/fonksiyon/sınıf isimleri İngilizce kalır (mevcut kod tabanı
  tutarlılığı).

## Mimari İnvariantlar (bkz. [[mimari]])

- `core/` paketi **asla** Qt (PySide6 veya başka bir UI framework)
  import etmez. Bu, `tests/test_00_core_has_no_qt_dependency.py` ile
  otomatik doğrulanır — bu testi geçmeyen bir değişiklik mimariyi bozmuş demektir.
- Yeni bir dönüşüm türü `core/converters/`'a **tek dosya** eklenerek
  tanımlanır ([[converter-ekleme]]); `ui_qml/bridge/app_bridge.py`'ye
  elle kayıt/dropdown-item eklenmez — `discovery.py` ve
  `AppBridge._categorize_converter()`'ın kural-tabanlı (sınıf adı/uzantı)
  kategorilendirmesi üzerinden otomatik.
- `core/` altındaki her klasörde `__init__.py` bulunur (normal paket).
  Olmazsa PyInstaller dinamik keşfedilen converter'ları paketlemez —
  bkz. [[paketleme]], `tests/test_packaging.py`.
- Konsol programı başlatan her `subprocess` çağrısı
  `creationflags=CREATE_NO_WINDOW` kullanır; aksi halde konsolsuz exe'de
  cmd pencereleri yanıp söner — bkz. [[paketleme]].
- Yeni converter, `IConverter`'ı doğrudan implemente etmek yerine
  `BaseConverter`'dan türetilir (bkz. [[converter-arayuzu]]) — ortak
  validate/timing/hata-sarmalama mantığı tekrar yazılmaz.

## Kod Stili

- Her yeni dosyanın docstring'inde hangi SOLID ilkesine hizmet ettiği
  kısaca belirtilir (mevcut desen: `SRP : ...`, `OCP : ...`).
- Yorumlar **WHY**'ı açıklar, **WHAT**'ı değil — iyi isimlendirme WHAT'ı
  zaten anlatır. "Bu satır X yapar" tarzı yorum yazılmaz; "LibreOffice
  bunsuz 'no export filter' hatası verir" gibi gizli bir kısıtı açıklayan
  yorum yazılır.
- Type hint'ler kullanılır (`Optional`, `List`, `Path`, dataclass'lar).
- Değer taşıyan nesneler (`ConversionResult`, `ConversionOptions`,
  `ConvertOutcome`) `@dataclass` olarak tanımlanır.
- `convert()`/`_do_convert()` içinde hata `Exception` olarak fırlatılır;
  onu `ConversionResult(success=False, ...)`'a çevirmek `BaseConverter`'ın
  işidir — UI katmanında dönüşüm mantığı için try/except yazılmaz.

## Test

- `core/`'a eklenen her yeni dönüşüm mantığı için `tests/` altına Qt
  gerektirmeyen bir pytest testi eklenir (bkz. [[test-ve-bagimliliklar]]).
  Gerçek harici motor gerektiren senaryolar `tests/_fakes.py`'deki
  `FakeConverter` deseniyle taklit edilir.
- Test eklemeden önce mevcut testlerin geçtiği doğrulanır: `python -m pytest tests/ -v`.

## Commit Kuralları

- Commit **yalnızca kullanıcı açıkça istediğinde** atılır.
- Commit mesajı Türkçe: kısa bir başlık satırı, gerekiyorsa madde
  madde (`-`) açıklama gövdesi.
- **Commit mesajlarında AI/asistan referansı bulunmaz** — `Co-Authored-By`
  gibi satırlar eklenmez.
- `git commit --no-verify`, `git push --force` gibi kontrolleri es geçen
  bayraklar kullanılmaz.
- Geniş kapsamlı `git add -A`'dan önce `git status` ile hangi dosyaların
  staged olduğu gözden geçirilir; olağandışı/hassas bir dosya varsa önce
  içeriği kontrol edilir.
- Yeni bir commit tercih edilir; `git commit --amend` yalnızca kullanıcı
  açıkça isterse kullanılır.

## Bilinçli Kapsam-Dışı Kararlar

Aşağıdakiler bilinerek ertelenmiştir, "unutulmuş" değildir:
- `ConversionOptions` tek düz bir "options bag" — hangi converter hangi
  alanı kullandığı yalnızca [[converter-arayuzu]] sayfasında belgeleniyor,
  arayüz seviyesinde zorlanmıyor.
- Plugin *paketleme* (setuptools entry_points, dış paket olarak converter
  yükleme) yok — dosya-bazlı keşif (`core/converters/` dizini) yeterli
  görülüyor.

## İlgili Sayfalar

- [[mimari]] — korunan mimari invariantlar
- [[converter-ekleme]] — bu kuralların pratikte uygulanışı
- [[test-ve-bagimliliklar]] — test kuralının detayı
