import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Otomatik Güncel Analiz Paneli")

# Veri kontrolü
DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.error("⚠️ Veri dosyası henüz oluşturulmamış. Lütfen 'Veriyi Şimdi Güncelle' butonuna basın veya sistemin otomatik çalışmasını bekleyin.")
    if st.button("🔄 Veriyi Şimdi Oluştur/Güncelle"):
        st.info("Veri çekme motoru başlatılıyor... Lütfen sayfayı 1 dakika sonra yenileyin.")
        # Buraya tetikleyici eklenebilir
else:
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    col1, col2 = st.columns(2)
    with col1:
        ligler = sorted(df['League'].unique())
        secilen_lig = st.selectbox("1️⃣ Lig Seçin", ligler)
    
    with col2:
        # Seçilen ligin gelecek maçlarını bülten olarak göster
        bugun = pd.Timestamp.now().strftime('%Y-%m-%d')
        bulten = df[(df['League'] == secilen_lig) & (df['Date'] >= bugun)].copy()
        
        if not bulten.empty:
            bulten['mac_adi'] = bulten['HomeTeam'] + " - " + bulten['AwayTeam']
            secilen_mac = st.selectbox("2️⃣ Bülten", bulten['mac_adi'].tolist())
            m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
        else:
            st.warning("Bu ligde yakında maç yok.")
            m = None

    if m is not None:
        st.divider()
        st.subheader(f"📊 {m['mac_adi']} ({m['RoundNumber']}. Hafta Analizi)")
        
        # AYNI HAFTA DÖNGÜSÜ ANALİZİ
        # Geçmiş maçları (Skoru olanları) filtrele
        gecmis = df[(df['League'] == secilen_lig) & (df['HomeScore'].notnull()) & (df['RoundNumber'] == m['RoundNumber'])]
        
        if not gecmis.empty:
            gecmis['Sonuç'] = gecmis['HomeScore'].astype(int).astype(str) + "-" + gecmis['AwayScore'].astype(int).astype(str)
            
            st.write(f"### {m['RoundNumber']}. Hafta Döngüsü Geçmiş Skorları")
            st.table(gecmis[['Date', 'HomeTeam', 'AwayTeam', 'Sonuç']])
            
            en_cok = gecmis['Sonuç'].value_counts().idxmax()
            st.success(f"💡 Bu döngüde en çok çıkan skor: **{en_cok}**")
        else:
            st.info("Bu haftaya ait henüz oynanmış maç verisi yok.")
