import sys
# Windows konsolunda Türkçe karakterlerin hata vermemesi için stdout reconfigure
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import math
import html
import streamlit as st
import streamlit.components.v1 as components
from database import SessionLocal
from models import Kitap, Ogrenci, OduncIslemi
from services import kitap_odunc_al, kitap_iade_et, kitaplari_getir

# ==============================================================================
# 1. MARKA VE SABİT GÖRSELLER (HOTLINK SORUNSUZ VE GÜVENİLİR CDN)
# ==============================================================================
# Wikipedia hotlink koruması engeline takılmayan, stabil eğitim ikonu
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/5354/5354060.png"

# Kırık veya boş kapaklar için belirlenen standart fallback görseli
FALLBACK_RESIM_URL = "https://dummyimage.com/150x225/e0e0e0/5c5c5c.png&text=Kapak+Yok"

st.set_page_config(
    page_title="Fırat Üniversitesi Kütüphane Sistemi",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. KURUMSAL BORDO TEMALI, GELİŞMİŞ VE KONTRAST-GARANTİLİ CSS (SaaS UI/UX)
# ==============================================================================
st.markdown(
    f"""
    <style>
    /* Google Fonts & Tipografi */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], section.main {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        scroll-behavior: smooth !important;
    }}

    /* Genel Sayfa Arka Planı */
    .stApp {{
        background-color: #F8FAFC;
    }}

    /* ------------------------------------------------------------- */
    /* 1. RENK VE KONTRAST HATALARI (INPUT LABEL & FORM STİLLERİ)     */
    /* ------------------------------------------------------------- */
    /* Giriş ekranındaki st.text_input label'ını her temada zorunlu koyu gri/siyah yap */
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stTextInput"] label span,
    div[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span {{
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.2px !important;
        margin-bottom: 4px !important;
    }}

    /* Giriş input kutusu stilleri */
    div[data-testid="stTextInput"] input {{
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 0.85rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: #8B0000 !important;
        box-shadow: 0 0 0 3px rgba(139, 0, 0, 0.15) !important;
    }}

    /* ------------------------------------------------------------- */
    /* 2. SOL MENÜ (SIDEBAR) VE ÖĞRENCİ PANELİ BEYAZ YAZI DÜZELTMESİ  */
    /* ------------------------------------------------------------- */
    section[data-testid="stSidebar"],
    .stSidebar,
    div[data-testid="stSidebarContent"] {{
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }}

    /* Sol menü genel başlık ve metinleri koyu gri/siyah (#1E293B) */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4,
    .stSidebar p, .stSidebar span, .stSidebar label {{
        color: #1E293B !important;
    }}

    /* Sidebar alt başlık ve bilgilendirme metinleri */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: #475569 !important;
    }}

    /* KRİTİK DÜZELTME: Öğrenci Paneli Bordo Kartındaki TÜM metinler ZORUNLU BEYAZ */
    .sidebar-profile-card,
    .sidebar-profile-card *,
    section[data-testid="stSidebar"] .sidebar-profile-card,
    section[data-testid="stSidebar"] .sidebar-profile-card *,
    div[data-testid="stSidebarUserContent"] .sidebar-profile-card,
    div[data-testid="stSidebarUserContent"] .sidebar-profile-card * {{
        color: #FFFFFF !important;
    }}

    .sidebar-profile-card {{
        background: linear-gradient(135deg, #7A0000 0%, #4D0000 100%) !important;
        padding: 1.3rem !important;
        border-radius: 14px !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 8px 22px rgba(122, 0, 0, 0.28) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
    }}

    .sidebar-profile-card h3 {{
        color: #FFFFFF !important;
        margin: 0 0 0.5rem 0 !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.22) !important;
        padding-bottom: 0.45rem !important;
    }}

    .sidebar-profile-card p,
    .sidebar-profile-card b,
    .sidebar-profile-card span {{
        color: #FFFFFF !important;
        font-size: 0.88rem !important;
        margin: 0.25rem 0 !important;
    }}

    /* Üzerimdeki Kitaplar Kartı */
    .sidebar-book-card {{
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px;
        padding: 0.85rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }}

    .sidebar-book-title {{
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        line-height: 1.35;
        margin-bottom: 0.3rem;
    }}

    .sidebar-book-date {{
        font-size: 0.78rem !important;
        color: #475569 !important;
        line-height: 1.4;
        margin-bottom: 0.5rem;
    }}

    /* ------------------------------------------------------------- */
    /* 3. GİRİŞ (LOGIN) EKRANI VE LOGO                               */
    /* ------------------------------------------------------------- */
    .login-container {{
        max-width: 480px;
        margin: 2.5rem auto 1rem auto;
        padding: 2.5rem 2rem;
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 20px 45px rgba(107, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid #F1F5F9;
        text-align: center;
    }}

    .login-logo-box {{
        width: 80px;
        height: 80px;
        margin: 0 auto 1.2rem auto;
        background: #FFFFFF;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(107, 0, 0, 0.16);
        border: 2px solid #F1F5F9;
        padding: 8px;
    }}

    .login-logo-img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
    }}

    .login-title {{
        font-size: 1.6rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }}

    .login-subtitle {{
        font-size: 0.92rem;
        color: #64748B;
        margin-bottom: 1.8rem;
    }}

    .login-hint-card {{
        background-color: #FEF2F2;
        border: 1px dashed #FECACA;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-top: 1.5rem;
        text-align: left;
        font-size: 0.82rem;
        color: #991B1B;
    }}

    /* ------------------------------------------------------------- */
    /* 4. ÜST BANNER VE RESMİ EĞİTİM LOGOSU                          */
    /* ------------------------------------------------------------- */
    .header-banner {{
        text-align: center;
        padding: 2.2rem 1.5rem 1.8rem 1.5rem;
        margin-bottom: 1.8rem;
        background: linear-gradient(135deg, #6B0000 0%, #8B0000 45%, #420000 100%);
        border-radius: 18px;
        color: #FFFFFF;
        box-shadow: 0 14px 34px rgba(107, 0, 0, 0.28);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    }}

    .header-banner::before {{
        content: "";
        position: absolute;
        top: -40%;
        left: -20%;
        width: 140%;
        height: 180%;
        background: radial-gradient(circle, rgba(255,255,255,0.14) 0%, transparent 65%);
        pointer-events: none;
    }}

    .header-banner-content {{
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}

    .header-title-row {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 0.35rem;
    }}

    .header-logo {{
        height: 56px;
        width: 56px;
        object-fit: contain;
        background: #FFFFFF;
        border-radius: 50%;
        padding: 6px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
        border: 2px solid rgba(255, 255, 255, 0.85);
        transition: transform 0.25s ease;
    }}

    .header-logo:hover {{
        transform: scale(1.08) rotate(4deg);
    }}

    .header-banner h1 {{
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
    }}
    
    .header-banner p {{
        font-size: 1.05rem;
        color: #F8D7DA;
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
        font-weight: 400;
    }}

    .header-badges {{
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 0.4rem;
    }}

    .header-badge-item {{
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #FFFFFF;
    }}

    /* ------------------------------------------------------------- */
    /* 5. MODERN SAAS KİTAP KARTI (GÖLGELENDİRME VE HOVER ETKİSİ)     */
    /* ------------------------------------------------------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, border-color 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        margin-bottom: 0.85rem !important;
    }}

    /* Kartın üzerine gelindiğinde (hover) yukarı kalkması (translateY(-5px)) */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0 16px 32px rgba(107, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.06) !important;
        border-color: #CBD5E1 !important;
    }}

    /* Kitap Kapağı Alanı: Orijinal Oran ve Taşmayan Kapsayıcı */
    .book-cover-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 10px;
        height: 220px;
        overflow: hidden;
    }}

    .book-cover-img {{
        max-width: 100%;
        max-height: 204px;
        width: auto;
        height: auto;
        border-radius: 6px;
        object-fit: contain !important;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
        transition: transform 0.3s ease;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover .book-cover-img {{
        transform: scale(1.04);
    }}

    /* Kitap Başlığı */
    .book-title {{
        font-size: 0.92rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1.35;
        min-height: 2.6rem;
        margin-bottom: 0.4rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}

    /* Yazar Bilgisi */
    .book-meta {{
        font-size: 0.8rem;
        color: #64748B;
        margin-bottom: 0.35rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Stok Durumu Rozetleri */
    .stock-badge {{
        font-size: 0.78rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 0.65rem;
        letter-spacing: 0.2px;
    }}

    .stock-available {{
        color: #065F46;
        background-color: #D1FAE5;
        border: 1px solid #A7F3D0;
    }}

    .stock-low {{
        color: #9A3412;
        background-color: #FFEDD5;
        border: 1px solid #FED7AA;
    }}

    .stock-empty {{
        color: #991B1B;
        background-color: #FEE2E2;
        border: 1px solid #FECACA;
    }}

    /* Buton Tasarımları */
    div.stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.86rem;
        transition: all 0.22s ease-in-out;
        border: 1px solid #8B0000;
        color: #8B0000;
        background-color: #FFFFFF;
        padding: 0.45rem 0.8rem;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(135deg, #8B0000 0%, #6B0000 100%);
        color: #FFFFFF;
        border-color: #6B0000;
        box-shadow: 0 4px 14px rgba(139, 0, 0, 0.28);
    }}

    div.stButton > button:disabled {{
        background-color: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #94A3B8 !important;
        cursor: not-allowed;
        box-shadow: none !important;
    }}

    /* ------------------------------------------------------------- */
    /* 6. SAYFALAMA (PAGINATION) KONTROLLERİ VE BELİRGİN BUTONLAR    */
    /* ------------------------------------------------------------- */
    /* Aktif Sayfa Butonu (Primary Buton) Stilleri */
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, #8B0000 0%, #6B0000 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #6B0000 !important;
        box-shadow: 0 4px 14px rgba(107, 0, 0, 0.35) !important;
        font-weight: 700 !important;
    }}

    .pagination-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        margin-top: 1.5rem;
        margin-bottom: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 3. YARDIMCI VE VERİTABANI FONKSİYONLARI
# ==============================================================================
def scroll_to_top():
    """Sayfa geçişlerinde ekranın pürüzsüzce (smooth) en üste kaymasını sağlar."""
    components.html(
        """
        <script>
            try {
                var mainContainer = window.parent.document.querySelector('section.main');
                if (mainContainer) {
                    mainContainer.scrollTo({top: 0, behavior: 'smooth'});
                } else {
                    window.parent.scrollTo({top: 0, behavior: 'smooth'});
                }
            } catch(e) {
                console.log(e);
            }
        </script>
        """,
        height=0,
        width=0
    )

def get_toplam_kitap_sayisi():
    """Veritabanındaki toplam kayıtlı kitap sayısını döner."""
    db = SessionLocal()
    try:
        return db.query(Kitap).count()
    except Exception:
        return 0
    finally:
        db.close()

def get_ogrenci_odunc_kitaplar(ogrenci_id):
    """Giriş yapmış aktif öğrencinin henüz iade etmediği kitapları çeker."""
    db = SessionLocal()
    try:
        islemler = (
            db.query(OduncIslemi, Kitap)
            .join(Kitap, OduncIslemi.kitap_id == Kitap.id)
            .filter(
                OduncIslemi.ogrenci_id == ogrenci_id,
                OduncIslemi.iade_edildi_mi == False
            )
            .order_by(OduncIslemi.id.desc())
            .all()
        )
        return islemler
    except Exception as e:
        return []
    finally:
        db.close()

def format_kitap_resim_url(resim_url):
    """
    URL geçerliliğini kontrol eder. Boş, nan veya geçersiz linklerde
    doğrudan dummyimage fallback görselini döner. Amazon linklerini HTTPS yapar.
    """
    if not resim_url or not isinstance(resim_url, str):
        return FALLBACK_RESIM_URL
    temiz = resim_url.strip()
    if temiz.lower() in ("nan", "none", "", "null"):
        return FALLBACK_RESIM_URL
    # Modern tarayıcılarda mixed-content engeline takılmaması için amazon linklerini https yap
    if temiz.startswith("http://images.amazon.com"):
        temiz = "https://" + temiz[len("http://"):]
    elif not temiz.startswith("http://") and not temiz.startswith("https://"):
        return FALLBACK_RESIM_URL
    return temiz

def get_kitap_kapak_html(resim_url, baslik):
    """
    Kırık veya boş çıkan resimler için onerror ve Amazon'un 1x1 piksel
    şeffaf boş resimlerine karşı onload kontrolü barındıran şık HTML kapak bileşeni üretir.
    """
    url = format_kitap_resim_url(resim_url)
    guvenli_baslik = html.escape(baslik if baslik else "Kitap Kapağı")
    return f"""
    <div class="book-cover-container">
        <img src="{url}" 
             alt="{guvenli_baslik}" 
             class="book-cover-img" 
             loading="lazy"
             onload="if(this.naturalWidth <= 1 || this.naturalHeight <= 1){{ this.onerror=null; this.src='{FALLBACK_RESIM_URL}'; }}"
             onerror="this.onerror=null; this.src='{FALLBACK_RESIM_URL}';" />
    </div>
    """


# ==============================================================================
# 4. SESSION STATE VE BİLDİRİMLER
# ==============================================================================
if "aktif_ogrenci" not in st.session_state:
    st.session_state.aktif_ogrenci = None

if "sayfa" not in st.session_state:
    st.session_state.sayfa = 1

if "scroll_tetikle" not in st.session_state:
    st.session_state.scroll_tetikle = False

# Sayfa geçişi yapıldıysa tepeye kaydır
if st.session_state.scroll_tetikle:
    scroll_to_top()
    st.session_state.scroll_tetikle = False

# Bildirimlerin ekrana basılması
if "toast_mesaji" in st.session_state:
    st.toast(st.session_state["toast_mesaji"], icon="🎉")
    del st.session_state["toast_mesaji"]

if "basari_mesaji" in st.session_state:
    st.success(st.session_state["basari_mesaji"])
    del st.session_state["basari_mesaji"]

if "hata_mesaji" in st.session_state:
    st.error(st.session_state["hata_mesaji"])
    del st.session_state["hata_mesaji"]


# ==============================================================================
# 5. GİRİŞ EKRANI (LOGIN PORTALI)
# ==============================================================================
if st.session_state.aktif_ogrenci is None:
    col_sol, col_orta, col_sag = st.columns([1, 1.4, 1])
    
    with col_orta:
        st.markdown(
            f"""
            <div class="login-container">
                <div class="login-logo-box">
                    <img src="{LOGO_URL}" 
                         alt="Kütüphane Logosu" 
                         class="login-logo-img" />
                </div>
                <div class="login-title">Fırat Üniversitesi</div>
                <div class="login-subtitle">Kütüphane Yönetim Sistemi - Öğrenci Giriş Portalı</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            ogrenci_no_giris = st.text_input(
                "Öğrenci Numarası",
                placeholder="Örn: 2026001",
                help="Sistemde kayıtlı öğrenci numaranızı giriniz."
            )
            giris_butonu = st.form_submit_button("🚀 Giriş Yap", use_container_width=True)

            if giris_butonu:
                temiz_no = str(ogrenci_no_giris).strip()
                if not temiz_no:
                    st.error("Lütfen öğrenci numaranızı boş bırakmayınız.")
                else:
                    db = SessionLocal()
                    try:
                        bulunan_ogrenci = db.query(Ogrenci).filter(Ogrenci.ogrenci_no == temiz_no).first()
                        if bulunan_ogrenci:
                            st.session_state.aktif_ogrenci = {
                                "id": bulunan_ogrenci.id,
                                "ad_soyad": bulunan_ogrenci.ad_soyad,
                                "ogrenci_no": bulunan_ogrenci.ogrenci_no,
                                "ceza_durumu": bulunan_ogrenci.ceza_durumu
                            }
                            st.session_state["toast_mesaji"] = f"Hoş geldiniz, {bulunan_ogrenci.ad_soyad}!"
                            st.rerun()
                        else:
                            st.error(f"'{temiz_no}' numaralı öğrenci sistemde bulunamadı. Lütfen numarayı kontrol edip tekrar deneyiniz.")
                    except Exception as e:
                        st.error(f"Veritabanı bağlantı hatası: {e}")
                    finally:
                        db.close()

        # Test ve Kolaylık İçin Bilgilendirme Kutusu
        st.markdown(
            """
            <div class="login-hint-card">
                <b>💡 Test Öğrenci Numaraları:</b><br>
                Veritabanınızda kayıtlı öğrencilerden birinin numarasını girebilirsiniz:<br>
                <code>2026001</code>, <code>2026002</code>, <code>2026003</code> ... <code>2026020</code>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Giriş yapılmadığında ana portalın alt kısımlarını çalıştırma
    st.stop()


# ==============================================================================
# 6. GİRİŞ YAPILMIŞ ANA KÜTÜPHANE PORTALI
# ==============================================================================
aktif_ogrenci = st.session_state.aktif_ogrenci
if not aktif_ogrenci:
    st.stop()

# 6.1. Sol Menü (Sidebar): Profil (Net Beyaz Metinler), Çıkış Yap ve İade Paneli
oduncteki_kitaplar = get_ogrenci_odunc_kitaplar(ogrenci_id=aktif_ogrenci["id"])

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-profile-card">
            <h3>👤 Öğrenci Paneli</h3>
            <p><b>Ad Soyad:</b> {aktif_ogrenci['ad_soyad']}</p>
            <p><b>Öğrenci No:</b> {aktif_ogrenci['ogrenci_no']}</p>
            <p><b>Öğrenci ID:</b> #{aktif_ogrenci['id']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Çıkış Yap Butonu
    if st.button("🚪 Çıkış Yap", key="btn_cikis_yap", use_container_width=True):
        st.session_state.aktif_ogrenci = None
        st.session_state.sayfa = 1
        st.session_state["toast_mesaji"] = "Başarıyla çıkış yapıldı."
        st.rerun()

    st.markdown("---")
    st.subheader(f"📖 Üzerimdeki Kitaplar ({len(oduncteki_kitaplar)})")

    if oduncteki_kitaplar:
        st.caption("Aşağıdaki ödünç aldığınız kitapları tek tıkla kütüphaneye iade edebilirsiniz:")
        
        for islem, kitap in oduncteki_kitaplar:
            with st.container():
                st.markdown(
                    f"""
                    <div class="sidebar-book-card">
                        <div class="sidebar-book-title">📘 {kitap.baslik}</div>
                        <div class="sidebar-book-date">
                            ✍️ {kitap.yazar or 'Bilinmiyor'}<br>
                            📅 Veriliş: {islem.verilis_tarihi or 'Bugün'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Dinamik İade Et Butonu
                if st.button("🔄 İade Et", key=f"btn_iade_{islem.id}", use_container_width=True):
                    try:
                        kitap_iade_et(islem.id)
                        iade_bildirim = f"'{kitap.baslik}' kitabı başarıyla iade edildi!"
                        st.session_state["toast_mesaji"] = iade_bildirim
                        st.session_state["basari_mesaji"] = f"🔄 {iade_bildirim} Kütüphane stoku güncellendi."
                        st.rerun()
                    except Exception as e:
                        st.session_state["hata_mesaji"] = f"İade işlemi sırasında hata oluştu: {e}"
                        st.rerun()
                st.markdown("---")
    else:
        st.info("Şu anda üzerinizde ödünç alınmış bir kitap bulunmuyor.")


# 6.2. Sayfalama Hesaplamaları ve Kitap Verilerini Çekme (Tam 24 Kitap)
SAYFA_BASINA_KITAP = 24
toplam_kitap = get_toplam_kitap_sayisi()
toplam_sayfa = max(1, math.ceil(toplam_kitap / SAYFA_BASINA_KITAP))

# Sayfa sınır kontrolü
if st.session_state.sayfa > toplam_sayfa:
    st.session_state.sayfa = toplam_sayfa
if st.session_state.sayfa < 1:
    st.session_state.sayfa = 1

offset_degeri = (st.session_state.sayfa - 1) * SAYFA_BASINA_KITAP
kitaplar = kitaplari_getir(limit=SAYFA_BASINA_KITAP, offset=offset_degeri)


# 6.3. Ana Başlık Banner'ı (Resmi Eğitim Logosu İle)
st.markdown(
    f"""
    <div class="header-banner">
        <div class="header-banner-content">
            <div class="header-title-row">
                <img src="{LOGO_URL}" 
                     alt="Kütüphane Logosu" 
                     class="header-logo" />
                <h1>Fırat Üniversitesi Kütüphane Sistemi</h1>
            </div>
            <p>Kütüphane arşivimizdeki seçkin eserleri keşfedebilir, tek tıkla anında ödünç alabilirsiniz.</p>
            <div class="header-badges">
                <span class="header-badge-item">🏛️ Fırat Üniversitesi Kütüphanesi</span>
                <span class="header-badge-item">📚 Toplam {toplam_kitap} Eser</span>
                <span class="header-badge-item">📄 Sayfa {st.session_state.sayfa} / {toplam_sayfa}</span>
                <span class="header-badge-item">👤 Aktif: {aktif_ogrenci['ad_soyad']} ({aktif_ogrenci['ogrenci_no']})</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# 6.4. Kitapları 6 Kolon x 4 Satır (24 Kitap) Halinde Sergileme
if kitaplar:
    KOLON_SAYISI = 6  # Ekranda yan yana 6'lı kolon

    for i in range(0, len(kitaplar), KOLON_SAYISI):
        satir_kitaplari = kitaplar[i : i + KOLON_SAYISI]
        kolonlar = st.columns(KOLON_SAYISI)

        for col_idx, kitap in enumerate(satir_kitaplari):
            with kolonlar[col_idx]:
                with st.container(border=True):
                    # Kapak Fotoğrafı: Onerror Fallback ve Orijinal Oranlı Görsel
                    st.markdown(get_kitap_kapak_html(kitap.resim_url, kitap.baslik), unsafe_allow_html=True)

                    # Başlık: 30 karakterde kesme ve üzerine gelince tam adını gösteren tooltip
                    ham_baslik = kitap.baslik if kitap.baslik else "İsimsiz Kitap"
                    if len(ham_baslik) > 30:
                        gorunen_baslik = ham_baslik[:27] + "..."
                    else:
                        gorunen_baslik = ham_baslik

                    guvenli_ham_baslik = html.escape(ham_baslik)
                    guvenli_gorunen_baslik = html.escape(gorunen_baslik)

                    st.markdown(
                        f'<div class="book-title" title="{guvenli_ham_baslik}">{guvenli_gorunen_baslik}</div>',
                        unsafe_allow_html=True
                    )

                    # Yazar Bilgisi
                    yazar_adi = kitap.yazar if kitap.yazar else "Bilinmiyor"
                    guvenli_yazar = html.escape(yazar_adi)
                    st.markdown(
                        f'<div class="book-meta" title="{guvenli_yazar}">✍️ <b>Yazar:</b> {guvenli_yazar}</div>',
                        unsafe_allow_html=True
                    )

                    # Mevcut Stok Durumu ve Şık Rozetler
                    stok = kitap.mevcut_stok if kitap.mevcut_stok is not None else 0
                    if stok > 2:
                        stok_html = f'<div class="stock-badge stock-available">📦 Stok: {stok} adet</div>'
                    elif stok > 0:
                        stok_html = f'<div class="stock-badge stock-low">⚠️ Son {stok} adet!</div>'
                    else:
                        stok_html = '<div class="stock-badge stock-empty">❌ Stokta Yok</div>'
                    
                    st.markdown(stok_html, unsafe_allow_html=True)

                    # Dinamik Ödünç Al Butonu
                    buton_etiketi = "Tükendi" if stok <= 0 else "Ödünç Al"
                    buton_tiklandi = st.button(
                        buton_etiketi,
                        key=f"btn_odunc_{kitap.id}",
                        disabled=(stok <= 0),
                        use_container_width=True
                    )

                    # Butona Tıklandığında Gerçekleşecek Dinamik İşlemler
                    if buton_tiklandi:
                        if stok <= 0:
                            st.session_state["hata_mesaji"] = f"Üzgünüz, '{ham_baslik}' kitabının stoku tükenmiştir!"
                            st.rerun()
                        else:
                            try:
                                # Aktif öğrencinin ID'si ile kitap ödünç alınıyor
                                kitap_odunc_al(ogrenci_id=aktif_ogrenci["id"], kitap_id=kitap.id)
                                
                                basari_metni = f"'{gorunen_baslik}' kitabı başarıyla ödünç alındı!"
                                st.session_state["toast_mesaji"] = basari_metni
                                st.session_state["basari_mesaji"] = f"🎉 Harika! {basari_metni} Kalan Stok: {stok - 1}"
                                
                                # Stok miktarının ve sol menünün anında güncellenmesi için rerun yapılır
                                st.rerun()
                            except Exception as e:
                                st.session_state["hata_mesaji"] = f"Ödünç alma işlemi sırasında hata oluştu: {e}"
                                st.rerun()

    # ==============================================================================
    # 6.5. GELİŞTİRİLMİŞ, ORTALANMIŞ VE AKICI SAYFALAMA (PAGINATION) KONTROLLERİ
    # ==============================================================================
    st.markdown("---")

    # Bilgilendirme Satırı
    gosterilen_son = min(offset_degeri + len(kitaplar), toplam_kitap)
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 0.8rem; color: #475569; font-size: 0.92rem; font-weight: 600;">
            📚 Toplam <b>{toplam_kitap}</b> eser arasından <b>{offset_degeri + 1} - {gosterilen_son}</b> arası listeleniyor &nbsp;•&nbsp; Sayfa <b>{st.session_state.sayfa}</b> / <b>{toplam_sayfa}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Ortalanmış ve Belirgin Sayfalama Butonları
    # Düzen: [Boşluk] + [Önceki] + [1]...[5] + [Sonraki] + [Boşluk]
    col_bos_sol, col_pag_center, col_bos_sag = st.columns([1, 4.5, 1])

    with col_pag_center:
        pag_layout = [1.8] + [1] * toplam_sayfa + [1.8]
        pag_cols = st.columns(pag_layout)

        # Önceki Sayfa Butonu
        with pag_cols[0]:
            if st.button("◀ Önceki", disabled=(st.session_state.sayfa <= 1), use_container_width=True, key="btn_prev_page"):
                st.session_state.sayfa -= 1
                st.session_state.scroll_tetikle = True
                st.rerun()

        # Sayfa Numarası Butonları (1, 2, 3, 4, 5...)
        for idx, p_num in enumerate(range(1, toplam_sayfa + 1)):
            with pag_cols[idx + 1]:
                is_active = (p_num == st.session_state.sayfa)
                btn_label = f"• {p_num} •" if is_active else str(p_num)
                btn_type = "primary" if is_active else "secondary"
                if st.button(btn_label, key=f"btn_page_{p_num}", type=btn_type, use_container_width=True):
                    st.session_state.sayfa = p_num
                    st.session_state.scroll_tetikle = True
                    st.rerun()

        # Sonraki Sayfa Butonu
        with pag_cols[-1]:
            if st.button("Sonraki ▶", disabled=(st.session_state.sayfa >= toplam_sayfa), use_container_width=True, key="btn_next_page"):
                st.session_state.sayfa += 1
                st.session_state.scroll_tetikle = True
                st.rerun()

else:
    st.info("Kütüphane sisteminde bu sayfada listelenecek kitap bulunmuyor.")