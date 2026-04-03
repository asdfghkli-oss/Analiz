import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Hatasız Analiz", layout="wide")
st.title("🏟️ Profesyonel Analiz Paneli")

DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.error("⚠️ Veri dosyası (CSV) henüz GitHub'da oluşmamış. Lütfen Actions sekmesinden 'Run workflow' yapıp 1 dakika bekleyin.")
else:
    try:
        # Veriyi oku ve sütunları temizle
        df = pd.read_csv(DATA_FILE)
        df.columns = [str(c).lower().strip() for c in df.columns]

        # Veri kontrolü
        if 'league' not in df.columns:
            st.error("Dosya okunuyor ama içinde 'league' sütunu yok. Lütfen update_data.py dosyasını güncelleyin.")
            st.write("Mevcut Sütunlar:", list(df.columns))
            st.stop()

        # Tarih sütununu güvenli hale getir
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            df['tarih_str'] = df['date'].dt.strftime('%Y-%m-%d')

        # Arayüz
        ligler = sorted(df['league'].unique())
        secilen_lig = st.selectbox("1️⃣ Lig Seçin", ligler)

        bugun = pd.Timestamp.now().normalize()
        bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()

        if not bulten.empty:
            bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
            secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac_adi'].unique())
            m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]

            st.divider()
            st.subheader(f"📊 {secilen_mac} ({m['roundnumber']}. Hafta Analizi)")
            
            # Aynı haftadaki geçmiş maçları süz
            gecmis = df[(df['league'] == secilen_lig) & 
                        (df['homescore'].notnull()) & 
                        (df['roundnumber'] == m['roundnumber'])].copy()
            
            if not gecmis.empty:
                gecmis['skor'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
                st.table(gecmis[['tarih_str', 'hometeam', 'awayteam', 'skor']])
                st.success(f"📌 En sık biten skor: {gecmis['skor'].value_counts().idxmax()}")
            else:
                st.info("Bu hafta için geçmiş veri henüz yok.")
        else:
            st.warning("Bu ligde yakında maç görünmüyor.")

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
