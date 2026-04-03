import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Canlı Analiz", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Canlı Analiz")

# --- LİG AYARLARI ---
ligler = {
    "Süper Lig": "turkey-super-lig",
    "Premier League": "epl",
    "La Liga": "la-liga",
    "Serie A": "serie-a",
    "Bundesliga": "bundesliga",
    "Ligue 1": "ligue-1"
}

@st.cache_data(ttl=3600)
def veri_getir(lig_kod):
    try:
        url = f"https://fixturedownload.com/feed/json/{lig_kod}-2025"
        r = requests.get(url)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- ARAYÜZ ---
col1, col2 = st.columns(2)

with col1:
    secilen_lig = st.selectbox("1️⃣ Lig Seçin", list(ligler.keys()))
    lig_kod = ligler[secilen_lig]

df = veri_getir(lig_kod)

if not df.empty:
    # Sütun isimlerini kontrol et ve hataları önle
    date_col = 'Date' if 'Date' in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
    
    with col2:
        bugun = datetime.now().strftime('%Y-%m-%d')
        # Gelecek maçları (Bülten) bul
        bulten = df[df[date_col] >= bugun].copy()
        
        if not bulten.empty:
            bulten['mac'] = bulten['HomeTeam'] + " - " + bulten['AwayTeam']
            secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac'].tolist())
            m = bulten[bulten['mac'] == secilen_mac].iloc[0]
        else:
            st.warning("Bu ligde yakında maç görünmüyor.")
            m = None

    if m is not None:
        st.divider()
        st.subheader(f"📊 {m['mac']} (Hafta: {m['RoundNumber']})")
        
        # Geçmiş Döngü Analizi: Aynı hafta (RoundNumber) oynanmış maçları getir
        gecmis = df[(df['RoundNumber'] == m['RoundNumber']) & (df['HomeScore'].notnull())].copy()
        
        if not gecmis.empty:
            # Skorları oluştur (İY bilgisi bu API'de yoksa sadece MS üzerinden gider)
            gecmis['MS'] = gecmis['HomeScore'].astype(int).astype(str) + "-" + gecmis['AwayScore'].astype(int).astype(str)
            
            st.write(f"### {m['RoundNumber']}. Haftada Oynanmış Diğer Maçlar")
            
            # Tabloyu göster
            tablo_df = gecmis[[date_col, 'HomeTeam', 'AwayTeam', 'MS']]
            tablo_df.columns = ['Tarih', 'Ev Sahibi', 'Deplasman', 'Sonuç']
            st.table(tablo_df)
            
            # İstatistik
            en_cok = gecmis['MS'].value_counts().idxmax()
            st.info(f"💡 Bu hafta döngüsünde en sık biten skor: **{en_cok}**")
        else:
            st.error("Bu haftaya ait henüz oynanmış maç verisi internette bulunamadı.")
else:
    st.error("Veri çekilemedi. Lütfen daha sonra tekrar deneyin.")
