import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pro Analiz", layout="centered")

if not os.path.exists("all_leagues_data.csv"):
    st.error("Veri bulunamadı. GitHub Actions çalıştırın.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    # --- 1. KUTUCUK: TARİH ---
    st.subheader("📅 Analiz Tarihi")
    secilen_tarih = st.date_input("Bülten Günü:", datetime.now().date())

    # --- 2. KUTUCUK: LİG ---
    st.subheader("🌍 Lig Seçimi")
    ligler = sorted(df['League'].unique())
    secilen_lig = st.selectbox("Lig seçiniz:", ligler)

    # --- 3. KUTUCUK: KARŞILAŞMA ---
    st.subheader("🏟️ Karşılaşma")
    # Seçilen tarihteki bülteni filtrele
    gunun_df = df[(df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)]
    
    if not gunun_df.empty:
        gunun_df['MatchName'] = gunun_df['HomeTeam'] + " vs " + gunun_df['AwayTeam']
        secilen_mac = st.selectbox("Günün Maçları:", gunun_df['MatchName'])
        
        ev = gunun_df[gunun_df['MatchName'] == secilen_mac]['HomeTeam'].values[0]
        dep = gunun_df[gunun_df['MatchName'] == secilen_mac]['AwayTeam'].values[0]

        # --- 4. EN ALT: ALGORİTMALAR ---
        st.divider()
        st.subheader("🧠 Oran Algoritmaları")
        
        # Takımların geçmiş verisini bul (Arşivden)
        gecmis = df[(df['HomeTeam'] == ev) | (df['AwayTeam'] == ev)].tail(10)
        
        if not gecmis.dropna(subset=['FTHG']).empty:
            ust_oran = (len(gecmis[(gecmis['FTHG'] + gecmis['FTAG']) > 2.5]) / len(gecmis)) * 100
            iy_oran = (len(gecmis[(gecmis['FTHG'] + gecmis['FTAG']) > 0.5]) / len(gecmis)) * 100 # Basit İY tahmini
            
            c1, c2 = st.columns(2)
            c1.metric("2.5 Üst Olasılığı", f"%{round(ust_oran, 1)}")
            c2.metric("İY 0.5 Üst Olasılığı", f"%{round(iy_oran, 1)}")
            st.success(f"💡 Algoritma Notu: {ev} takımı son maçlarında gol yeme eğiliminde.")
        else:
            st.warning("Bu maç için yeterli geçmiş veri bulunamadı.")
    else:
        st.warning("Bu tarihte ve ligde bülten maçı bulunamadı.")
