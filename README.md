# Mini Haber Okuyucu

Bu proje, Collect API kullanarak haberleri çekmek ve kullanıcıların haberleri okumalarını sağlayan bir masaüstü uygulamasıdır.

## Özellikler

* Haberleri ülke ve kategori seçerek çekme
* Haberleri liste halinde görüntüleme
* Haber detaylarını görüntüleme
* Haberleri tarayıcıda açma

## Kurulum

1. Projeyi klonlayın: `git clone https://github.com/berrin27/Mini-Haber-Okuyucu.git`
2. Projeyi açın ve `pip install -r requirements.txt` komutunu çalıştırın
3. `.env` dosyasını oluşturun ve `COLLECTAPI_KEY` değerini ekleyin
4. `python main.py` komutunu çalıştırın

## Kullanım

1. Uygulamayı çalıştırın
2. Ülke ve kategori seçin
3. "Haberleri Getir" butonuna tıklayın
4. Haberleri liste halinde görüntüleyin
5. Bir haber seçin ve detaylarını görüntüleyin
6. Haberleri tarayıcıda açın

## Teknolojiler

* Python 3.x
* Tkinter
* SQLite
* Requests
* PIL (Python Imaging Library)
* Collect API

## Contributing

Projeye katkıda bulunmak istiyorsanız, lütfen bir pull request açın.