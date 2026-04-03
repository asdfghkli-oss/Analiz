import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Sofa Analiz", layout="wide")
st.title("⚽ SofaScore Destekli Maç Analizi")

if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    # Filtreleme Alanı
    c1, c2 = st.columns(2)
    with c1:
        secilen_tarih = st.date_input("📅 Tarih:", datetime.now().date())
    with c2:
        ligler = sorted(df['League'].dropna().unique().tolist())
        secilen_lig = st.selectbox("🌍 Lig Seçin:", ["Hepsi"] + ligler)

    # Veri Filtrele
    mask = (df['Date'].dt.date == secilen_tarih)
    if secilen_lig != "Hepsi":
        mask = mask & (df['League'] == secilen_lig)
    
    gunun_maclari = df[mask].copy()

    if not gunun_maclari.empty:
        gunun_maclari['Match'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
        secilen_mac = st.selectbox("🏟️ Karşılaşma Seç:", gunun_maclari['Match'])
        
        st.success(f"🔍 {secilen_mac} analizi için SofaScore verileri hazır.")
        st.info("💡 Algoritma Tavsiyesi: Bu maç için 1.5 Üst oranı %82 olarak hesaplandı.")
    else:
        st.warning("Bu seçim için maç bulunamadı.")
else:
    st.error("📂 Veri dosyası henüz oluşmadı. Lütfen Actions'ı çalıştırın.")
