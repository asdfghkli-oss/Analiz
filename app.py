import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("⚽ Profesyonel Maç Analiz Sistemi")

# Dosya kontrolü
if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    # Sütun ismini büyük harf 'Date' olarak eşitle
    df['Date'] = pd.to_datetime(df['Date'])

    # --- KUTUCUKLAR ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📅 1. TARİH SEÇİMİ")
        secilen_tarih = st.date_input("Analiz günü:", datetime.now().date())

    with col2:
        st.info("🌍 2. LİG SEÇİMİ")
        ligler = sorted(df['League'].unique())
        secilen_lig = st.selectbox("Bir lig seçin:", ligler)

    # --- MAÇ LİSTESİ ---
    st.divider()
    mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
    gunun_maclari = df[mask].copy()

    if not gunun_maclari.empty:
        gunun_maclari['MatchName'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
        secilen_mac = st.selectbox("🤝 3. KARŞILAŞMA SEÇİN:", gunun_maclari['MatchName'])
        
        # Algoritma Gösterimi
        st.success(f"🔍 {secilen_mac} için analizler hazırlanıyor...")
    else:
        st.warning(f"Seçilen tarihte ({secilen_tarih}) {secilen_lig} bülteni bulunamadı.")
else:
    st.error("⚠️ Veri henüz çekilmemiş. Lütfen GitHub Actions üzerinden 'Run workflow' yapın.")
