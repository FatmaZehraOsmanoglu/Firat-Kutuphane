#Sınıflarımızı/Nesnelerimizi tanımlayacağımız dosyamız
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base

# --- ÜST SINIF (MİRAS VERECEK) ---
class Kullanici(Base):
    __abstract__ = True # Veritabanında "kullanici" diye bir tablo oluşmayacak
    
    id = Column(Integer, primary_key=True, index=True)
    ad_soyad = Column(String)

# --- ALT SINIFLAR ---
class Ogrenci(Kullanici):
    __tablename__ = "ogrenciler"
    
    ogrenci_no = Column(String, unique=True)
    ceza_durumu = Column(Float, default=0.0)

class Yonetici(Kullanici):
    __tablename__ = "yoneticiler"
    
    sicil_no = Column(String, unique=True)

# --- BAĞIMSIZ SINIFLAR ---
class Kitap(Base):
    __tablename__ = "kitaplar"
    
    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String)
    yazar = Column(String)
    resim_url = Column(String) # YENİ EKLEDİĞİMİZ SÜTUN
    toplam_stok = Column(Integer)
    mevcut_stok = Column(Integer)

class OduncIslemi(Base):
    __tablename__ = "odunc_islemleri"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ForeignKey ile bu sütunların diğer tablolardaki 'id'lere işaret ettiğini belirtiyoruz
    kitap_id = Column(Integer, ForeignKey("kitaplar.id"))
    ogrenci_id = Column(Integer, ForeignKey("ogrenciler.id"))
    
    # Tarihleri şimdilik basitlik adına String (Metin) olarak tutuyoruz
    verilis_tarihi = Column(String)
    teslim_tarihi = Column(String)
    iade_edildi_mi = Column(Boolean, default=False)