import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("⚽ Pro Analiz Paneli")

if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date']) # HATA ÇÖZÜLDÜ: 'Date' artık büyük harf.

    # 1. KUTUCUK: TARİH
    secilen_tarih = st.date_input("Analiz Tarihi:", datetime.now().date())

    # 2. KUTUCUK: LİG
    ligler = sorted(df['League'].unique())
    secilen_lig = st.selectbox("Lig Seç:", ligler)

    # 3. KUTUCUK: MAÇ
    mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
    gunun_maclari = df[mask]

    if not gunun_maclari.empty:
        mac_adi = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
        secilen_mac = st.selectbox("Maç Seç:", mac_adi)
        
        # 4. EN ALT: ALGORİTMA
        st.divider()
        st.subheader("🧠 Oran Algoritması")
        # Burada seçilen maçın analizi yapılacak
        st.write(f"Seçilen Maç: {secilen_mac} için veriler hesaplanıyor...")
    else:
        st.warning("Bu tarihte seçili lig için maç bulunamadı.")
else:
    st.error("Veri dosyası henüz oluşmadı. GitHub Actions'ı çalıştırın.")
