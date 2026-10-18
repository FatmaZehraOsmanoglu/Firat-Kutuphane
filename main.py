from database import engine, Base
import models

# --- VERİTABANI VE TABLOLARI OLUŞTURMA (Hatanın Çözümü) ---
# Bu satır, models.py dosyasındaki sınıflara bakar (yeni eklediğimiz resim_url dahil)
# ve kutuphane.db dosyasını tablolarıyla birlikte sıfırdan kusursuzca yaratır.
Base.metadata.create_all(bind=engine)

print("Harika! Veritabanı ve tablolar başarıyla oluşturuldu.")