from database import SessionLocal
from models import Kitap, OduncIslemi, Ogrenci
from datetime import datetime
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def kitap_odunc_al(ogrenci_id, kitap_id):
    db = SessionLocal()
    
    # 1. Önce istenen kitabı ve öğrenciyi veritabanında bulalım
    kitap = db.query(Kitap).filter(Kitap.id == kitap_id).first()
    ogrenci = db.query(Ogrenci).filter(Ogrenci.id == ogrenci_id).first()

    if not kitap:
        print("Hata: Böyle bir kitap bulunamadı.")
        db.close()
        return
        
    if not ogrenci:
        print("Hata: Böyle bir öğrenci bulunamadı. Lütfen önce öğrenci kaydı oluşturun.")
        db.close()
        return

    # 2. Stok Kontrolü
    if kitap.mevcut_stok > 0:
        # Stokta var, işlemi yap
        kitap.mevcut_stok -= 1  # Stoku 1 azalt
        
        # Günün tarihini al (örnek: "2026-10-17")
        bugun = datetime.now().strftime("%Y-%m-%d")
        
        yeni_islem = OduncIslemi(
            kitap_id=kitap.id, 
            ogrenci_id=ogrenci.id, 
            verilis_tarihi=bugun, 
            teslim_tarihi="2026-11-01" # Şimdilik örnek bir teslim tarihi veriyoruz
        )
        
        db.add(yeni_islem)
        db.commit()
        print(f"Başarılı! '{kitap.baslik}' adlı kitap, {ogrenci.ad_soyad} isimli öğrenciye ödünç verildi.")
        print(f"Kalan Stok: {kitap.mevcut_stok}")
    else:
        print(f"Üzgünüz, '{kitap.baslik}' kitabının stoku tükenmiş.")
        
    db.close()

def ogrenci_ekle(ad_soyad, ogrenci_no):
    db = SessionLocal()
    
    yeni_ogrenci = Ogrenci(
        ad_soyad=ad_soyad, 
        ogrenci_no=ogrenci_no, 
        ceza_durumu=0.0
    )
    
    db.add(yeni_ogrenci)
    db.commit()
    print(f"Sisteme yeni öğrenci eklendi: {ad_soyad}")
    db.close()

from models import OduncIslemi # Dosyanın üst kısmındaki importlara OduncIslemi'ni de eklemeyi unutma

def kitap_iade_et(islem_id):
    db = SessionLocal()
    
    # 1. Veritabanından o ödünç alma kaydını buluyoruz
    islem = db.query(OduncIslemi).filter(OduncIslemi.id == islem_id).first()
    
    if not islem:
        print("Hata: Böyle bir ödünç işlemi sistemde bulunamadı.")
        db.close()
        return
        
    if islem.iade_edildi_mi:
        print("Bu kitap zaten daha önceden iade edilmiş.")
        db.close()
        return
        
    # 2. İlgili kitabı bul, durumu güncelle ve stoku geri artır
    kitap = db.query(Kitap).filter(Kitap.id == islem.kitap_id).first()
    
    islem.iade_edildi_mi = True
    kitap.mevcut_stok += 1
    
    # Değişiklikleri veritabanına kaydet
    db.commit()
    print(f"İade Başarılı! '{kitap.baslik}' kitabı kütüphaneye geri döndü.")
    print(f"Yeni Kalan Stok: {kitap.mevcut_stok}")
    
    db.close()

def kitaplari_getir(limit=24, offset=0):
    """Veritabanından belirli aralıktaki (offset ve limit) kitapları çeker."""
    db = SessionLocal()
    try:
        return db.query(Kitap).offset(offset).limit(limit).all()
    finally:
        db.close()