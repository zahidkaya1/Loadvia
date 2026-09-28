# Loadvia

Loadvia, YouTube, Instagram, X/Twitter, TikTok, Facebook ve Threads gibi platformlardan medya indirmeyi kolaylaştırmak amacıyla geliştirilmiş bir Windows masaüstü uygulamasıdır.

**Güncel kararlı sürüm:** `v1.3.1`

## ✨ Öne Çıkan Özellikler

- Video, fotoğraf ve çoklu medya indirme
- Instagram carousel içeriklerinde medya seçimi
- İndirme kuyruğu
- Başarısız işlemleri yeniden deneme
- Panodan bağlantı algılama
- İndirme klasörü seçimi
- Kalite ve format seçimi
- WhatsApp uyumlu MP4 çıktısı
- Tarayıcı oturumu yönetimi
- Setup ve Portable dağıtım seçenekleri
- Windows 10 ve Windows 11 desteği

## 🌐 Desteklenen Platformlar

| Platform | Durum |
| --- | --- |
| YouTube | ✅ Destekleniyor |
| Instagram | ✅ Destekleniyor |
| X / Twitter | ✅ Destekleniyor |
| TikTok | ✅ Destekleniyor |
| Facebook | ✅ Destekleniyor |
| Threads | ✅ Destekleniyor |
| Kick | 🕒 Planlanıyor |

## 🔐 Oturum Merkezi

Instagram ve Threads gibi oturum gerektirebilen platformlar için tarayıcı oturumları Loadvia içerisinden yönetilebilir.

Desteklenen tarayıcılar:

- Google Chrome
- Mozilla Firefox
- Microsoft Edge
- Brave
- Opera
- Opera GX
- Vivaldi

Oturum Merkezi üzerinden:

- Tarayıcıdan oturum alma
- Çerez dosyasından oturum alma
- Aktif oturum kaynağını görüntüleme
- Profil bilgisini görüntüleme
- İçe aktarma zamanını görüntüleme
- Oturumu test etme
- Kayıtlı oturum verilerini kaldırma

işlemleri gerçekleştirilebilir.

## 🔒 Güvenlik ve Gizlilik

- Loadvia önce oturumsuz indirme yöntemini dener.
- Gerektiğinde kullanıcı tarafından içe aktarılan oturum bilgileri kullanılabilir.
- Yalnızca gerekli Instagram ve Threads oturum verileri kalıcı olarak saklanır.
- Oturum bilgileri kullanıcıya özel olarak Windows üzerinde korunur.
- Çerez değerleri uygulama arayüzünde gösterilmez.
- Kayıtlı oturum verileri kullanıcı tarafından Oturum Merkezi üzerinden silinebilir.

## 📦 Kurulum

### Setup

`Loadvia-Setup-1.3.1.exe` dosyasını çalıştırarak Loadvia'yı Windows'a kurabilirsiniz.

Kurulum işlemi:

- Uygulama dosyalarını sisteme yükler
- Başlat menüsüne kısayol ekler
- Loadvia'nın standart masaüstü uygulaması olarak kullanılmasını sağlar

### Portable

`Loadvia-1.3.1-windows-x64-portable.zip` arşivi kurulum gerektirmeden kullanılabilir.

Arşivi çıkardıktan sonra:

`Loadvia.exe`

dosyasını çalıştırmanız yeterlidir.

Portable sürümde uygulama ayarları kendi dizininde saklanır ve uygulama USB bellek gibi taşınabilir ortamlardan çalıştırılabilir.

## ▶️ Kullanım

1. Desteklenen bir platformdan bağlantıyı kopyalayın.
2. Bağlantıyı Loadvia'ya yapıştırın.
3. Loadvia'nın içeriği analiz etmesini bekleyin.
4. Format ve kalite seçeneklerini belirleyin.
5. İndirme konumunu seçin.
6. İndirmeyi başlatın.

Oturum gerektiren içeriklerde Oturum Merkezi kullanılabilir.

## 🆕 Son Sürüm — v1.3.1

- YouTube kalite seçimi geliştirildi.
- HTTP 403 hatalarına karşı indirme akışı iyileştirildi.
- Video uyumluluk işlemleri geliştirildi.
- İlerleme çubuğu arayüzü iyileştirildi.
- Video probe işlemleri daha kararlı hale getirildi.
- Instagram carousel seçim ekranı daha kompakt ve kullanışlı hale getirildi.

Tüm sürüm geçmişi için [`CHANGELOG.md`](CHANGELOG.md) dosyasını inceleyebilirsiniz.

## ⚠️ Kapsam Sınırları

Loadvia internetteki her içeriğin indirilebileceğini garanti etmez.

İndirme desteği aşağıdaki faktörlere bağlıdır:

- Platformun mevcut yapısı
- Erişim izinleri
- Oturum gereksinimleri
- Altyapı bileşenlerinin desteği

Özel hesap içerikleri, silinmiş paylaşımlar, coğrafi olarak kısıtlanmış içerikler ve DRM korumalı yayınlar indirilemeyebilir.

Loadvia'yı yalnızca sahibi olduğunuz, açıkça indirme izniniz bulunan veya hukuken indirme hakkına sahip olduğunuz içerikler için kullanın.

## 💻 Sistem Gereksinimleri

- Windows 10
- Windows 11

## 🛠️ Geliştirici Kurulumu

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
