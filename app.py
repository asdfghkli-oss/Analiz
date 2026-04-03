import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Akıllı Analiz Paneli", layout="wide")
st.title("🏟️ Akıllı Analiz Paneli")

DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.warning("⚠️ Veri dosyası henüz oluşmadı. GitHub Actions üzerinden 'Run workflow' yapın.")
else:
    df = pd.read_csv(DATA_FILE)
    
    # Tarih formatını zorla düzelt (Kritik hata buradaydı)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['tarih_str'] = df['date'].dt.strftime('%Y-%m-%d')
    
    col1, col2 = st.columns(2)
    with col1:
        ligler = sorted(df['league'].unique())
        secilen_lig = st.selectbox("1️⃣ Ligi Seçin", ligler)
    
    with col2:
        bugun = pd.Timestamp.now().normalize()
        # Bülten: Bugün ve sonrası
        bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
        
        if not bulten.empty:
            bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
            secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac_adi'].unique())
            m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
        else:
            st.info("Bu ligde yakında maç görünmüyor.")
            m = None

    if m is not None:
        st.divider()
        st.subheader(f"📊 {secilen_mac} | {m['roundnumber']}. Hafta Analizi")
        
        # ANALİZ: Aynı hafta döngüsündeki geçmiş maçlar
        gecmis = df[(df['league'] == secilen_lig) & 
                    (df['homescore'].notnull()) & 
                    (df['roundnumber'] == m['roundnumber'])].copy()
        
        if not gecmis.empty:
            gecmis['skor'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
            st.write(f"🔍 {secilen_lig} Geçmiş {m['roundnumber']}. Hafta Skorları:")
            st.table(gecmis[['tarih_str', 'hometeam', 'awayteam', 'skor']])
            
            en_cok = gecmis['skor'].value_counts().idxmax()
            st.success(f"💡 Bu hafta döngüsünde en sık biten skor: **{en_cok}**")
        else:
            st.info("Bu haftaya ait geçmiş sonuç bulunamadı.")
