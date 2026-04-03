import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz Arşivi", layout="wide")
st.title("🏟️ 20+ Lig Geniş Analiz Paneli")

DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.info("🔄 Veritabanı oluşturuluyor... Lütfen GitHub Actions sekmesinden işlemi başlatın veya bitmesini bekleyin.")
else:
    df = pd.read_csv(DATA_FILE)
    
    # Küçük harf standardı uygula
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Tarih dönüşümü
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df['tarih_str'] = df['date'].dt.strftime('%Y-%m-%d')

    # Arayüz
    col1, col2 = st.columns(2)
    with col1:
        # LİGLER ARTIK BURADA DOLU GELECEK
        lig_listesi = sorted(df['league'].unique())
        secilen_lig = st.selectbox("1️⃣ Analiz Edilecek Ligi Seçin", lig_listesi)
    
    with col2:
        bugun = pd.Timestamp.now().normalize()
        bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
        
        if not bulten.empty:
            # Maç seçimi için isim oluştur
            bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
            secilen_mac = st.selectbox("2️⃣ Güncel Bülten Maçı", bulten['mac_adi'].unique())
            m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
        else:
            st.warning("Bu ligde yakında maç bulunmuyor.")
            m = None

    if m is not None:
        st.divider()
        # HAFTA ANALİZİ
        hafta = m['roundnumber']
        st.subheader(f"📊 {secilen_mac} | {hafta}. Hafta Döngüsü")
        
        # Geçmiş maçları bul
        gecmis = df[(df['league'] == secilen_lig) & 
                    (df['homescore'].notnull()) & 
                    (df['roundnumber'] == hafta)].copy()
        
        if not gecmis.empty:
            gecmis['skor'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
            st.write(f"🔍 {secilen_lig} geçmişindeki {hafta}. hafta sonuçları:")
            st.table(gecmis[['tarih_str', 'hometeam', 'awayteam', 'skor']])
            
            # En çok çıkan skor
            skor_ozet = gecmis['skor'].value_counts()
            en_cok = skor_ozet.idxmax()
            st.success(f"📌 İstatistik: Bu döngüde en sık alınan skor: **{en_cok}**")
        else:
            st.info("Bu hafta döngüsüne ait geçmiş maç sonucu henüz veritabanında yok.")
