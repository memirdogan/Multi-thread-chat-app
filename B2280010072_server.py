#!/usr/bin/env python3
"""
Chat Sunucusu - Ağ Sistemleri Ödevi
Öğrenci No: B2280010072
"""

import socket
import threading

# Ayarlar
IP = '127.0.0.1'  # localhost
PORT = 5000  # TCP port
YAYIN_GRUP = '224.0.0.1'  # multicast grup
YAYIN_PORT = 5001  # multicast port

# Bağlı kullanıcılar listesi
kullanicilar = {}  # {adres: (soket, isim)}
kilit = threading.Lock()  # thread güvenliği için

def mesaj_gonder(mesaj, gonderen=None):
    """Tüm kullanıcılara mesaj gönder"""
    with kilit:
        for adres, (soket, _) in list(kullanicilar.items()):
            if adres != gonderen:  # kendine gönderme
                try:
                    soket.send(mesaj.encode('utf-8'))
                except:
                    # Bağlantı kopmuşsa kullanıcıyı sil
                    kullanici_sil(adres)

def kullanici_sil(adres):
    """Kullanıcıyı listeden sil"""
    with kilit:
        if adres in kullanicilar:
            isim = kullanicilar[adres][1]
            soket = kullanicilar[adres][0]
            
            try:
                soket.close()
            except:
                pass
            
            del kullanicilar[adres]
            print(f"{isim} çıkış yaptı")
            
            # Diğer kullanıcılara bildir
            mesaj_gonder(f"[SERVER] {isim} sohbetten ayrıldı!")

def istemci_isle(istemci_soket, adres):
    """İstemci bağlantısını işle"""
    try:
        # Kullanıcı adı iste
        istemci_soket.send("Kullanıcı adınız: ".encode('utf-8'))
        isim = istemci_soket.recv(1024).decode('utf-8').strip()
        
        # Kullanıcıyı listeye ekle
        with kilit:
            kullanicilar[adres] = (istemci_soket, isim)
        
        # Herkese duyur
        mesaj_gonder(f"[SERVER] {isim} sohbete katıldı!", adres)
        print(f"Yeni kullanıcı: {isim}")
        
        # Mesajları dinle
        while True:
            veri = istemci_soket.recv(1024).decode('utf-8')
            if not veri:
                break
            
            print(f"{isim}: {veri}")
            
            # Komut kontrolü
            if veri.startswith('/'):
                komut_isle(veri, adres)
            else:
                # Normal mesaj
                mesaj_gonder(f"{isim}: {veri}", adres)
                
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        kullanici_sil(adres)

def komut_isle(komut, adres):
    """Komutları işle"""
    parcalar = komut.split()
    komut_adi = parcalar[0].lower()
    isim = kullanicilar[adres][1]
    
    if komut_adi == '/cikis':
        kullanici_sil(adres)
        
    elif komut_adi == '/ozel' and len(parcalar) >= 3:
        hedef = parcalar[1]
        mesaj = ' '.join(parcalar[2:])
        ozel_mesaj_gonder(isim, hedef, mesaj)
        
    elif komut_adi == '/yayin' and len(parcalar) >= 2:
        mesaj = ' '.join(parcalar[1:])
        yayin_gonder(f"{isim} (YAYIN): {mesaj}")
        
    elif komut_adi == '/liste':
        liste = "Bağlı kullanıcılar: " + ", ".join([k[1] for k in kullanicilar.values()])
        kullanicilar[adres][0].send(liste.encode('utf-8'))
        
    elif komut_adi == '/yardim':
        yardim = """
        Komutlar:
        /ozel <kullanıcı> <mesaj> - Özel mesaj
        /yayin <mesaj> - Herkese yayın
        /liste - Kullanıcıları listele
        /cikis - Çıkış yap
        /yardim - Yardım
        """
        kullanicilar[adres][0].send(yardim.encode('utf-8'))
    else:
        kullanicilar[adres][0].send("Bilinmeyen komut. /yardim yazın.".encode('utf-8'))

def ozel_mesaj_gonder(gonderen, hedef, mesaj):
    """Özel mesaj gönder"""
    hedef_adres = None
    
    # Hedef kullanıcıyı bul
    with kilit:
        for adres, (_, isim) in kullanicilar.items():
            if isim == hedef:
                hedef_adres = adres
                break
    
    if hedef_adres:
        # Hedefe mesaj gönder
        ozel = f"[ÖZEL - {gonderen}'dan]: {mesaj}"
        kullanicilar[hedef_adres][0].send(ozel.encode('utf-8'))
        
        # Gönderene bilgi ver
        for adres, (_, isim) in kullanicilar.items():
            if isim == gonderen:
                bilgi = f"[ÖZEL - {hedef}'e]: {mesaj}"
                kullanicilar[adres][0].send(bilgi.encode('utf-8'))
                break
    else:
        # Kullanıcı bulunamadı
        for adres, (_, isim) in kullanicilar.items():
            if isim == gonderen:
                kullanicilar[adres][0].send(f"Kullanıcı '{hedef}' bulunamadı.".encode('utf-8'))
                break

def yayin_gonder(mesaj):
    """Multicast yayın gönder"""
    try:
        yayin_soket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        yayin_soket.sendto(mesaj.encode('utf-8'), (YAYIN_GRUP, YAYIN_PORT))
        print(f"Yayın gönderildi: {mesaj}")
    except Exception as e:
        print(f"Yayın hatası: {e}")

def main():
    # TCP sunucu soketi
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((IP, PORT))
        server.listen(5)  # en fazla 5 bağlantı beklet
        print(f"Sunucu başladı: {IP}:{PORT}")
        print(f"Yayın adresi: {YAYIN_GRUP}:{YAYIN_PORT}")
        
        while True:
            istemci, adres = server.accept()
            print(f"Bağlantı: {adres[0]}:{adres[1]}")
            
            # Her istemci için yeni thread
            t = threading.Thread(target=istemci_isle, args=(istemci, adres))
            t.daemon = True
            t.start()
            
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        # Tüm bağlantıları kapat
        for adres in list(kullanicilar.keys()):
            kullanici_sil(adres)
        
        if server:
            server.close()

if __name__ == "__main__":
    main()