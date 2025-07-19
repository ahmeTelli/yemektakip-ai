# yemektakip-ai

Goru Restoran – Bilgisayarlı Görü ile Akıllı Restoran Takip Sistemi
Proje Hakkında
Bu proje, bir restoranda masalara gelen yemeklerin ve garsonların performansının bilgisayarlı görü ile otomatik olarak takip edilmesini amaçlıyor.
Sistemde masaların üzerindeki kameralar sayesinde hangi yemeğin geldiği tespit edilip anlık olarak fiyat hesaplanıyor. Aynı zamanda garsonların hangi masaya baktığı, ne kadar sürede hizmet verdiği ve performansları da kaydediliyor.

Python, PyQt6 ile masaüstü arayüzü yazıldı.

YOLOv8 ile gerçek zamanlı yemek tespiti yapılıyor.

Siparişler, garsonlar ve masalar SQLite veritabanında saklanıyor.

QR kod ile masanın açılışı ve kapanışı hızlıca yapılabiliyor.

Garsonun gecikmesi gibi durumlarda sistem otomatik olarak puan düşürüyor.

Tüm veriler rapor ekranında görüntülenebiliyor.

Özellikler
Masaya gelen yemeklerin otomatik tanınması ve ücretlendirilmesi

Garsonların performans takibi ve puanlama sistemi

Masa açma/kapama işlemlerinin QR kod ile yapılabilmesi

Tüm siparişlerin ve garson performanslarının aylık raporlanması

Kurulum
Gerekli Python paketlerini yükleyin:

pip install -r requirements.txt
Ana dosyayı başlatın:

python util.py
(Kendi modelinizi kullanacaksanız YOLOv8 ağırlık dosyanızı models/ klasörüne ekleyin.)

Kullanım
Program açıldıktan sonra “Kamera Başlat” butonuna tıklayın.

Sisteme video veya webcam üzerinden veri gönderebilirsiniz.

Masaya yemek gelince otomatik olarak ekrana yansır, fiyat ve garson bilgisi güncellenir.

Masada işlem bitince QR kod okutarak hesabı kapatabilirsiniz.

“Rapor” butonuyla geçmiş tüm işlemleri görüntüleyebilirsiniz.

Katkıda Bulunanlar
Ahmet Telli

[youtube](https://youtu.be/GewHmj34BSk)

Proje tamamen eğitim ve demo amaçlı geliştirilmiştir.
