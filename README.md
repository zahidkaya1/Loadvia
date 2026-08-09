# Loadvia

YouTube, Instagram, X/Twitter, TikTok, Facebook ve Threads gibi platformlardan medya indirmeyi kolaylaştıran Windows masaüstü uygulaması.

Güncel kararlı sürüm: **v1.2.1**

## Desteklenen Platformlar

- YouTube — Destekleniyor
- Instagram — Destekleniyor
- X / Twitter — Destekleniyor
- TikTok — Destekleniyor
- Facebook — Destekleniyor
- Threads — Destekleniyor
- Kick — Planlanıyor

## Temel Özellikler

- Video indirme
- MP4 video ve MP3 ses indirme
- Oynatma listesi desteği
- İndirme kuyruğu
- İndirme klasörü seçimi
- Başarısız işlemleri yeniden deneme
- Panodan bağlantı algılama
- Otomatik medya uyumluluk seçenekleri
- WhatsApp uyumlu MP4 seçeneği
- Windows masaüstü arayüzü

## Oturum Merkezi

Instagram ve Threads gibi oturum gerektirebilen platformlar için tarayıcı oturumları Loadvia içinden yönetilebilir.

Desteklenen tarayıcı altyapısı:
- Google Chrome
- Mozilla Firefox
- Microsoft Edge
- Brave
- Opera
- Opera GX
- Vivaldi

Ayrıca:
- Çerez Dosyasıyla Al
- Aktif oturum kaynağı
- Profil bilgisi
- İçe aktarma zamanı
- Oturumu Test Et
- Oturum Verilerini Kaldır

## Güvenlik / Gizlilik

- Loadvia önce oturumsuz indirmeyi dener.
- Gerektiğinde kullanıcı tarafından içe aktarılan oturum kullanılabilir.
- Kalıcı olarak yalnız gerekli Threads/Instagram oturum verileri saklanır.
- Oturum bilgileri kullanıcıya özel olarak Windows üzerinde korunur.
- Çerez değerleri arayüzde gösterilmez.
- Kullanıcı Oturum Merkezi'nden kayıtlı oturum verilerini kaldırabilir.

## Kurulum

### Setup
`Loadvia-Setup-1.2.1.exe`
Normal Windows kurulumu isteyen kullanıcılar için.

### Portable
`Loadvia-1.2.1-windows-x64-portable.zip`
Kurulum yapmadan kullanmak isteyenler için. Portable ZIP çıkarıldıktan sonra `Loadvia.exe` çalıştırılır.

## Kullanım

1. Bağlantıyı kopyala/yapıştır.
2. Loadvia bağlantıyı analiz etsin.
3. Format/kalite seçeneklerini seç.
4. İndirme konumunu belirle.
5. İndirmeyi başlat.

Oturum gereken içeriklerde Oturum Merkezi kullanılabilir.

## Son Sürüm — v1.2.1

- Geliştirilmiş Oturum Merkezi
- Çoklu tarayıcı oturum desteği
- Çerez Dosyasıyla Al yardım akışı
- Aktif oturum kaynağı, profili ve tarihi
- Tarayıcı kapatıp tekrar deneme sistemi
- Oturum güvenliği ve kararlılık iyileştirmeleri

Detaylı geçmiş için CHANGELOG.md dosyasına göz atabilirsiniz.

## Kapsam Sınırı

Uygulama internetteki her içeriği garanti ederek indiremez. Destek; sitenin yapısına, erişim izinlerine ve altyapı bileşenlerine bağlıdır. Özel hesap içerikleri, silinmiş paylaşımlar, coğrafi kısıtlamalar ve DRM ile korunan yayınlar indirilemeyebilir.

Uygulamayı yalnızca sahibi olduğunuz, açıkça indirme izniniz bulunan veya hukuken indirme hakkınız olan içerikler için kullanın.

## Gereksinimler

- Windows 10 veya Windows 11

## Kurulum (Geliştirici)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
