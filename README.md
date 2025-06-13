# Çok İstemcili Chat Uygulaması
**Öğrenci No:** B2280010072

## Ne İşe Yarar?
Bu uygulama, birden fazla kullanıcının aynı anda bağlanıp mesajlaşabildiği bir chat programıdır. Kullanıcılar hem herkese mesaj gönderebilir hem de özel mesajlaşabilir.

## Nasıl Çalışır?
- Sunucu sürekli çalışır ve istemcilerin bağlanmasını bekler
- Her istemci için ayrı bir thread oluşturulur
- İstemciler TCP üzerinden sunucuya bağlanır
- Multicast mesajlar UDP üzerinden gönderilir

## Dosyalar
- `B2280010072_server.py`: Sunucu programı
- `B2280010072_client.py`: İstemci programı

## Nasıl Çalıştırılır?

### Sunucu
```bash
python3 B2280010072_server.py
```

### İstemci
```bash
python3 B2280010072_client.py
```

## Kullanılabilir Komutlar
- `/ozel <kullanıcı> <mesaj>`: Özel mesaj gönder
- `/yayin <mesaj>`: Herkese yayın gönder
- `/liste`: Bağlı kullanıcıları göster
- `/yardim`: Komutları göster
- `/cikis`: Bağlantıyı kes

## Teknik Bilgiler
- Programlama Dili: Python 3
- Kullanılan Modüller: socket, threading
- İletişim Protokolleri: TCP (unicast), UDP (multicast)
- Sunucu IP: 127.0.0.1 (localhost)
- TCP Port: 5000
- Multicast Grup: 224.0.0.1
- Multicast Port: 5001

## Notlar
- Programı çalıştırmadan önce sunucuyu başlatmayı unutmayın
- Aynı ağdaki farklı bilgisayarlardan bağlanmak için sunucu IP adresini değiştirin
