import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Arşiv")

# Dosya kontrolü
if not os.path.exists("all_leagues_data.csv"):
    st.error("⚠️ Veri henüz çekilmedi. GitHub Actions'a gidip 'Run workflow' yapmalısın.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # Tarih kolonunu güvenli hale getir
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['tarih_str'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # Arayüz
    secilen_lig = st.selectbox("1️⃣ Lig Seçin", sorted(df['league'].unique()))
    
    bugun = pd.Timestamp.now().normalize()
    bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
    
    if not bulten.empty:
        bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
        secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac_adi'].unique())
        m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
        
        st.divider()
        st.subheader(f"📊 {secilen_mac} ({m['roundnumber']}. Hafta Analizi)")
        
        # AYNI HAFTA DÖNGÜSÜNDEKİ GEÇMİŞ MAÇLAR
        gecmis = df[(df['league'] == secilen_lig) & 
                    (df['homescore'].notnull()) & 
                    (df['roundnumber'] == m['roundnumber'])].copy()
        
        if not gecmis.empty:
            gecmis['skor'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
            st.table(gecmis[['tarih_str', 'hometeam', 'awayteam', 'skor']])
            st.success(f"📌 İstatistik: Bu haftada en çok çıkan skor: {gecmis['skor'].value_counts().idxmax()}")
        else:
            st.info("Bu ligin bu haftasına ait geçmiş veri henüz yüklenmemiş.")
    else:
        st.warning("Bu lig için yakında maç bulunmuyor.")
