import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Canlı Analiz Paneli", layout="wide")
st.title("⚽ Yapay Zeka Destekli Canlı Analiz")

# --- VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=3600) # Verileri 1 saat önbelleğe alarak hızı artırır
def veri_cek(lig_kodu):
    try:
        url = f"https://fixturedownload.com/feed/json/{lig_kodu}-2025"
        r = requests.get(url)
        return pd.DataFrame(r.json())
    except:
        return pd.DataFrame()

# --- LİG AYARLARI ---
ligler = {
    "Süper Lig": "turkey-super-lig",
    "Premier League": "epl",
    "La Liga": "la-liga",
    "Serie A": "serie-a",
    "Bundesliga": "bundesliga",
    "Ligue 1": "ligue-1",
    "Eredivisie": "eredivisie"
}

# --- ARAYÜZ ---
col1, col2 = st.columns(2)

with col1:
    secilen_lig_ad = st.selectbox("1️⃣ Lig Seçin", list(ligler.keys()))
    lig_kodu = ligler[secilen_lig_ad]

# Veriyi İnternetten Çek
df = veri_cek(lig_kodu)

if not df.empty:
    # Tarih formatını düzenle
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    with col2:
        # Sadece bugün ve gelecek maçları "Bülten" olarak filtrele
        bugun = datetime.now().strftime('%Y-%m-%d')
        bulten = df[df['Date'] >= bugun]
        
        if not bulten.empty:
            bulten['mac_adi'] = bulten['HomeTeam'] + " - " + bulten['AwayTeam']
            secilen_mac = st.selectbox("2️⃣ Güncel Bülten (Maç Seçin)", bulten['mac_adi'].tolist())
            m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
            hedef_takim = m['HomeTeam']
            hedef_round = m['RoundNumber']
        else:
            st.warning("Bu ligde yakın zamanda maç bulunamadı.")
            hedef_takim = None

    st.divider()

    # --- ANALİZ MOTORU ---
    if hedef_takim:
        st.subheader(f"📊 {hedef_takim} - {m['AwayTeam']} ({hedef_round}. Hafta Analizi)")
        
        # Geçmiş maçları (Oynanmış olanları) filtrele
        gecmis = df[df['HomeScore'].notnull()]
        
        # Haftalık Döngü: Geçmişte aynı haftada (RoundNumber) oynanan maçları bul
        dongu_verisi = gecmis[gecmis['RoundNumber'] == hedef_round]
        
        if not dongu_verisi.empty:
            # İY ve MS Skorlarını Oluştur (API'den gelen verilere göre)
            # Not: Bu API genelde MS skorunu verir, eğer İY skoru yoksa MS üzerinden analiz yapar
            dongu_verisi['Skor'] = dongu_verisi['HomeScore'].astype(int).astype(str) + " - " + dongu_verisi['AwayScore'].astype(int).astype(str)
            
            st.write(f"### {hedef_round}. Haftada Diğer Takımlar Ne Yapmış?")
            
            # Tablo Gösterimi
            display_df = dongu_verisi[['Date', 'HomeTeam', 'AwayTeam', 'Skor']].copy()
            display_df.columns = ['Tarih', 'Ev Sahibi', 'Deplasman', 'Maç Sonucu']
            st.table(display_df)
            
            # İstatistiksel Özet
            en_cok_skor = dongu_verisi['Skor'].value_counts().idxmax()
            st.success(f"💡 Bu hafta döngüsünde en sık görülen skor: **{en_cok_skor}**")
            
            # KG ve Alt/Üst Tahmini (Basit Algoritma)
            toplam_gol = dongu_verisi['HomeScore'].astype(int) + dongu_verisi['AwayScore'].astype(int)
            ust_yuzde = (len(toplam_gol[toplam_gol > 2.5]) / len(toplam_gol)) * 100
            
            c1, c2 = st.columns(2)
            c1.metric("2.5 Üst Olasılığı", f"%{ust_yuzde:.0f}")
            c2.metric("Ortalama Gol", f"{toplam_gol.mean():.2f}")
            
        else:
            st.info("Bu hafta numarasına ait henüz oynanmış maç verisi bulunmuyor.")
else:
    st.error("Veri çekilemedi. Lütfen internet bağlantınızı veya lig seçimini kontrol edin.")
