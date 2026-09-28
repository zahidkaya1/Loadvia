# Changelog
Tüm önemli değişiklikler bu dosyada belgelenmektedir.

## [1.3.1] - 2026-08-14
### İyileştirildi
- YouTube kalite seçimi, seçilen maksimum çözünürlüğü aşmayacak şekilde iyileştirildi.
- Instagram çoklu medya/carousel seçim ekranı daha kullanışlı ve kompakt hale getirildi.
- Uzun video uyumluluk işlemlerinde ilerleme çubuğu hareketli işlem durumunu gösterecek şekilde iyileştirildi.

### Düzeltildi
- Bazı YouTube indirmelerinde oluşan HTTP 403 hatasına neden olan indirme akışı düzeltildi.
- Video codec bilgilerinin bazı durumlarda UNKNOWN görünmesine yol açan codec probe hatası düzeltildi.
- Video uyumluluk dönüşümü daha kararlı hale getirildi.
- YouTube kalite seçiminin istenen sınırın üzerinde formata düşebilmesine yol açabilecek fallback davranışı engellendi.

## [1.3.0] - 2026-08-12
### Yeni
- Instagram tek fotoğraf indirme desteği.
- Instagram fotoğraf/video carousel desteği.
- Carousel içerisindeki medyaları tek tek seçebilmek için medya seçici arayüzü.
- Karma fotoğraf/video carousel desteği.

### İyileştirmeler
- Kalite/format seçenekleri ortak ve daha tutarlı bir yapıya getirildi.
- Carousel dosya adlarında gönderideki orijinal medya sırası korunuyor.

### Düzeltmeler
- MP3 kalite seçimiyle ilgili indirme sorunları giderildi.

## [1.2.1]
### Eklendi & İyileştirildi
- Geliştirilmiş Oturum Merkezi
- Platform bazlı oturum ve indirme durumları
- Aktif oturum kaynağı ve profil bilgisi
- Google Chrome / Firefox / Edge / Brave / Opera / Opera GX / Vivaldi tarayıcı oturumu içe aktarma altyapısı
- Tarayıcıyı Kapat ve Tekrar Dene akışı
- Güvenli PID/executable-path tabanlı browser process izolasyonu
- Çerez Dosyasıyla Al ve kullanıcı dostu yardım akışı
- SessionStore schema v2 metadata
- v1.2.0 session verileriyle geriye dönük uyumluluk
- Yerel tarih/saat gösterimi
- Oturum ve UI regresyon düzeltmeleri

## [1.2.0]
### Eklendi & İyileştirildi
- Oturum Merkezi eklendi
- Windows DPAPI ile güvenli yerel oturum saklama
- Firefox'tan oturum alma
- Netscape cookie dosyası içe aktarma
- Threads ve Instagram için merkezi oturum altyapısı
- Threads /share/ bağlantılarının canonical gönderi adresine çözülmesi
- tarayıcı profil fallback döngülerinin sadeleştirilmesi
- geçici cookie dosyalarının güvenli yaşam döngüsü

## [1.1.1] - 2026-08-06
### Eklenenler & Düzeltilenler
- Bütün MP4 indirmelerinde otomatik H.264/AAC uyumluluğu sağlandı.
- Uyumsuz videoların güvenli şekilde MP4 biçimine dönüştürülmesi eklendi.
- Threads normal ve kuyruk indirmelerinde format fallback düzeltmesi yapıldı.
- Firefox aktif profil algılama iyileştirmesi eklendi.
- MP3 ve MP4 dosyalarında ortak sıra numarası kullanılması düzeltmesi eklendi.
- Alt işlemlerde siyah CMD/PowerShell pencerelerinin görünmesi engellendi.

## [1.1.0] - 2026-08-04

### Eklendi

- Facebook video ve Reels desteği
- Threads video desteği
- Otomatik, Firefox, Chrome, Edge ve Brave oturum seçenekleri
- Netscape çerez dosyası desteği
- İndirme hızı sınırı

### İyileştirildi

- Tarayıcı profili ve oturum algılama
- Oturum gerektiren içeriklerde hata mesajları
- İndirme kuyruğunda oturum bilgilerinin korunması
- Sosyal medya bağlantısı algılama
- Geçmiş ekranında platform gösterimi
- Threads tek video ve çoklu video ayrımı

### Düzeltildi

- Aynı Threads videosunun farklı kaynaklar nedeniyle birden fazla video olarak görünmesi
- Chrome çerez veritabanı hatalarında tekrarlanan başarısız denemeler
- Threads test dosyasındaki sözdizimi bozulması
- Çeşitli arayüz ve hata mesajı sorunları

### Bilinen Sorunlar

- Bazı Threads bağlantılarında indirme kuyruğu, seçilen video formatını yeniden bulamayabilir.
- Kick indirme desteği bu sürüme dahil değildir.

## [1.0.0]

İlk kararlı sürüm.
