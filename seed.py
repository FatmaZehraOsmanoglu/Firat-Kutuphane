import pandas as pd
import random
from database import SessionLocal
from models import Kitap, Ogrenci

def veritabanini_doldur():
    print("CSV dosyası okunuyor...")
    try:
        df = pd.read_csv('kitaplar.csv', sep=';', on_bad_lines='skip', encoding='latin-1')
    except Exception as e:
        print(f"Dosya okuma hatası: {e}")
        return
        
    db = SessionLocal()
    
    # --- 1. KİTAPLARI EKLEME ---
    print("Veritabanına rastgele stoklu kitaplar ekleniyor...")
    eklenen_kitap_sayisi = 0
    for index, row in df.head(100).iterrows():
        baslik = str(row['Book-Title'])
        yazar = str(row['Book-Author'])
        resim = str(row['Image-URL-M'])
        
        # 1 ile 7 arasında rastgele bir stok sayısı belirliyoruz
        rastgele_stok = random.randint(1, 7)
        
        yeni_kitap = Kitap(
            baslik=baslik, 
            yazar=yazar, 
            resim_url=resim,
            toplam_stok=rastgele_stok, 
            mevcut_stok=rastgele_stok
        )
        db.add(yeni_kitap)
        eklenen_kitap_sayisi += 1
        
    # --- 2. ÖĞRENCİLERİ EKLEME ---
    print("Sisteme 20 yeni öğrenci ekleniyor...")
    for i in range(1, 21):
        # 2026001, 2026002 ... 2026020 şeklinde numaralar üretir
        ogrenci_no = f"2026{i:03d}" 
        
        yeni_ogrenci = Ogrenci(
            ad_soyad=f"Öğrenci {i}",
            ogrenci_no=ogrenci_no,
            ceza_durumu=0.0
        )
        db.add(yeni_ogrenci)
        
    # Tüm değişiklikleri veritabanına kaydet
    db.commit()
    db.close()
    
    print(f"Harika! {eklenen_kitap_sayisi} kitap ve 20 öğrenci başarıyla eklendi.")

if __name__ == "__main__":
    veritabanini_doldur()