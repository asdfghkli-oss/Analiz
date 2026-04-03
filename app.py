import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz Arşivi", layout="wide")
st.title("🏟️ 20+ Lig Akıllı Analiz")

DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.warning("⚠️ Veri dosyası henüz oluşmadı. GitHub Actions'dan 'Run workflow' yapın.")
else:
    df = pd.read_csv(DATA_FILE)
    # Sütunları küçük harfe çevirerek eşleştir
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # Tarih kontrolü ve dönüşümü
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['tarih_str'] = df['date'].dt.strftime('%Y-%m-%d')
    else:
        st.error("Hata: Veri dosyasında 'date' sütunu bulunamadı!")
        st.stop()

    # Lig ve Maç Seçimi
    ligler = sorted(df['league'].unique())
    secilen_lig = st.selectbox("1️⃣ Lig Seçin", ligler)
    
    bugun = pd.Timestamp.now().normalize()
    bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
    
    if not bulten.empty:
        bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
        secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac_adi'].unique())
        m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
        
        st.divider()
        st.subheader(f"📊 {secilen_mac} | Hafta: {m['roundnumber']}")
        
        # Geçmiş hafta döngüsü analizi
        gecmis = df[(df['league'] == secilen_lig) & (df['homescore'].notnull()) & 
                    (df['roundnumber'] == m['roundnumber'])].copy()
        
        if not gecmis.empty:
            gecmis['skor'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
            st.table(gecmis[['tarih_str', 'hometeam', 'awayteam', 'skor']])
            st.success(f"📌 En sık biten skor: {gecmis['skor'].value_counts().idxmax()}")
        else:
            st.info("Bu haftaya ait geçmiş sonuç yok.")
