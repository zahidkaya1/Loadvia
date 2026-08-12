# Loadvia

YouTube, Instagram, X/Twitter, TikTok, Facebook ve Threads gibi platformlardan medya indirmeyi kolaylaştıran Windows masaüstü uygulaması.

Güncel kararlı sürüm: **v1.3.0**

## Desteklenen Platformlar

- YouTube — Destekleniyor
- Instagram — Destekleniyor
- X / Twitter — Destekleniyor
- TikTok — Destekleniyor
- Facebook — Destekleniyor
- Threads — Destekleniyor
- Kick — Planlanıyor

## Temel Özellikler

- Instagram tek fotoğraf indirme
- Instagram çoklu fotoğraf/video (carousel) indirme
- Carousel içeriklerinde istenen medyaları seçebilme
- İndirme kuyruğu
- İndirme klasörü seçimi
- Başarısız işlemleri yeniden deneme
- Panodan bağlantı algılama
- Sadeleştirilmiş kalite ve format seçenekleri
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
`Loadvia-Setup-1.3.0.exe`
Normal Windows kurulumu isteyen kullanıcılar için.

### Portable
`Loadvia-1.3.0-windows-x64-portable.zip`
Kurulum yapmadan kullanmak isteyenler için. Portable ZIP çıkarıldıktan sonra `Loadvia.exe` çalıştırılır.

## Kullanım

1. Bağlantıyı kopyala/yapıştır.
2. Loadvia bağlantıyı analiz etsin.
3. Format/kalite seçeneklerini seç.
4. İndirme konumunu belirle.
5. İndirmeyi başlat.

Oturum gereken içeriklerde Oturum Merkezi kullanılabilir.

## Son Sürüm — v1.3.0

- Instagram tek fotoğraf indirme desteği eklendi
- Instagram fotoğraf/video carousel indirme desteği eklendi
- Carousel içinden istenilen medyaları tek tek seçebilme özelliği eklendi (Fotoğraf + Video karışık carousel desteği)
- Orijinal medya sırasını koruyan dosya adlandırması eklendi
- Video ve ses indirmeleri için kalite/format seçenekleri daha sade ve ortak bir yapıya geçirildi
- Ses/MP3 kalite seçimiyle ilgili indirme sorunları giderildi

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
