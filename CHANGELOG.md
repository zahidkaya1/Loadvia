# Changelog
Tüm önemli değişiklikler bu dosyada belgelenmektedir.

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
# DeÄŸiÅŸiklik GÃ¼nlÃ¼ÄŸÃ¼

## [1.1.0] - 2026-08-04

### Eklendi

- Facebook video ve Reels desteÄŸi
- Threads video desteÄŸi
- Otomatik, Firefox, Chrome, Edge ve Brave oturum seÃ§enekleri
- Netscape Ã§erez dosyasÄ± desteÄŸi
- Ä°ndirme hÄ±zÄ± sÄ±nÄ±rÄ±

### Ä°yileÅŸtirildi

- TarayÄ±cÄ± profili ve oturum algÄ±lama
- Oturum gerektiren iÃ§eriklerde hata mesajlarÄ±
- Ä°ndirme kuyruÄŸunda oturum bilgilerinin korunmasÄ±
- Sosyal medya baÄŸlantÄ±sÄ± algÄ±lama
- GeÃ§miÅŸ ekranÄ±nda platform gÃ¶sterimi
- Threads tek video ve Ã§oklu video ayrÄ±mÄ±

### DÃ¼zeltildi

- AynÄ± Threads videosunun farklÄ± kaynaklar nedeniyle birden fazla video olarak gÃ¶rÃ¼nmesi
- Chrome Ã§erez veritabanÄ± hatalarÄ±nda tekrarlanan baÅŸarÄ±sÄ±z denemeler
- Threads test dosyasÄ±ndaki sÃ¶zdizimi bozulmasÄ±
- Ã‡eÅŸitli arayÃ¼z ve hata mesajÄ± sorunlarÄ±

### Bilinen Sorunlar

- BazÄ± Threads baÄŸlantÄ±larÄ±nda indirme kuyruÄŸu, seÃ§ilen video formatÄ±nÄ± yeniden
  bulamayabilir.
- Kick indirme desteÄŸi bu sÃ¼rÃ¼me dahil deÄŸildir.

## [1.0.0]

Ä°lk kararlÄ± sÃ¼rÃ¼m.
