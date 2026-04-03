import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Akıllı Analiz Paneli")

DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.warning("⚠️ Veri dosyası henüz oluşturulmadı. GitHub Actions üzerinden 'Run workflow' yapın.")
else:
    df = pd.read_csv(DATA_FILE)
    # Sütun isimlerini her ihtimale karşı tekrar temizle
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Tarih formatını zorla düzelt
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    else:
        st.error("Kritik hata: Veri dosyasında tarih sütunu bulunamadı.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        ligler = sorted(df['league'].unique())
        secilen_lig = st.selectbox("1️⃣ Lig Seçin", ligler)
    
    with col2:
        bugun = pd.Timestamp.now().normalize()
        # Bülten: Bugün ve sonrası
        bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
        
        if not bulten.empty:
            bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
            secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac_adi'].unique())
            m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
        else:
            st.warning("Bu ligde yakında maç yok.")
            m = None

    if m is not None:
        st.divider()
        st.subheader(f"📊 {secilen_mac} ({m['roundnumber']}. Hafta Analizi)")
        
        # Geçmiş maçlar (Aynı hafta numarası ve skoru olanlar)
        gecmis = df[(df['league'] == secilen_lig) & 
                    (df['homescore'].notnull()) & 
                    (df['roundnumber'] == m['roundnumber'])].copy()
        
        if not gecmis.empty:
            gecmis['sonuc'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
            st.write(f"🔍 {m['roundnumber']}. Hafta Geçmiş Skorları:")
            st.table(gecmis[['date_str', 'hometeam', 'awayteam', 'sonuc']])
            
            en_cok = gecmis['sonuc'].value_counts().idxmax()
            st.success(f"💡 Bu döngüde en sık görülen skor: **{en_cok}**")
        else:
            st.info("Bu hafta döngüsüne ait geçmiş veri bulunamadı.")
