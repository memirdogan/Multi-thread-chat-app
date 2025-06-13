#!/usr/bin/env python3
"""
Chat İstemcisi - Ağ Sistemleri Ödevi
Öğrenci No: B2280010072
"""

import socket
import threading

# Ayarlar
SUNUCU = '127.0.0.1'
PORT = 5000
YAYIN_GRUP = '224.0.0.1'
YAYIN_PORT = 5001

class ChatIstemci:
    def __init__(self):
        # Soketleri oluştur
        self.ana_soket = None
        self.yayin_soket = None
        self.kullanici_adi = None
        self.calisiyor = True
    
    def baglanti_kur(self):
        """Sunucuya bağlan"""
        try:
            # Ana soket (TCP)
            self.ana_soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ana_soket.connect((SUNUCU, PORT))
            
            # Yayin soketi kur
            self.yayin_dinleyici_kur()
            
            return True
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False
    
    def yayin_dinleyici_kur(self):
        """Multicast dinleyici kur"""
        try:
            # UDP soket oluştur
            self.yayin_soket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.yayin_soket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Rastgele port kullan (çakışma olmasın)
            try:
                self.yayin_soket.bind(('', YAYIN_PORT))
            except:
                self.yayin_soket.bind(('', 0))
                print("Farklı port kullanılıyor")
            
            # Multicast grubuna katıl
            try:
                grup = socket.inet_aton(YAYIN_GRUP)
                mreq = socket.inet_aton(YAYIN_GRUP) + socket.inet_aton('0.0.0.0')
                self.yayin_soket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            except:
                print("Yayın grubuna katılınamadı")
            
        except Exception as e:
            print(f"Yayın dinleyici hatası: {e}")
    
    def basla(self):
        """İstemciyi başlat"""
        if not self.baglanti_kur():
            return False
        
        # Kullanıcı adı al
        istek = self.ana_soket.recv(1024).decode('utf-8')
        print(istek, end='')
        self.kullanici_adi = input()
        self.ana_soket.send(self.kullanici_adi.encode('utf-8'))
        
        # Mesaj alma thread'i
        t1 = threading.Thread(target=self.mesaj_al)
        t1.daemon = True
        t1.start()
        
        # Yayın alma thread'i
        t2 = threading.Thread(target=self.yayin_al)
        t2.daemon = True
        t2.start()
        
        # Hoşgeldin mesajı
        print(f"\nSohbete hoş geldin, {self.kullanici_adi}!")
        print("Komutlar için /yardim yazabilirsin")
        
        # Mesaj gönderme döngüsü
        self.mesaj_gonder()
        
        return True
    
    def mesaj_al(self):
        """Sunucudan gelen mesajları al"""
        while self.calisiyor:
            try:
                mesaj = self.ana_soket.recv(1024).decode('utf-8')
                if not mesaj:
                    print("Sunucu bağlantısı kesildi")
                    self.kapat()
                    break
                print(mesaj)
            except:
                if self.calisiyor:
                    print("Mesaj alma hatası")
                break
    
    def yayin_al(self):
        """Yayın mesajlarını al"""
        while self.calisiyor:
            try:
                veri, adres = self.yayin_soket.recvfrom(1024)
                mesaj = veri.decode('utf-8')
                print(f"\n{mesaj}")
                print("> ", end='', flush=True)
            except:
                if self.calisiyor:
                    print("Yayın alma hatası")
                break
    
    def mesaj_gonder(self):
        """Kullanıcıdan mesaj al ve gönder"""
        while self.calisiyor:
            try:
                mesaj = input("> ")
                if mesaj.lower() == "/cikis":
                    self.ana_soket.send("/cikis".encode('utf-8'))
                    self.kapat()
                    break
                elif mesaj.strip():  # Boş mesaj gönderme
                    self.ana_soket.send(mesaj.encode('utf-8'))
            except KeyboardInterrupt:
                self.kapat()
                break
            except:
                if self.calisiyor:
                    print("Mesaj gönderme hatası")
                self.kapat()
                break
    
    def kapat(self):
        """Bağlantıyı kapat"""
        self.calisiyor = False
        
        if self.ana_soket:
            try:
                self.ana_soket.close()
            except:
                pass
        
        if self.yayin_soket:
            try:
                self.yayin_soket.close()
            except:
                pass
        
        print("Bağlantı kapatıldı")

if __name__ == "__main__":
    # İstemciyi başlat
    try:
        istemci = ChatIstemci()
        istemci.basla()
    except KeyboardInterrupt:
        print("\nProgram sonlandırıldı")
    except Exception as e:
        print(f"\nHata: {e}")