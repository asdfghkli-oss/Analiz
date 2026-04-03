import streamlit as st
import pandas as pd
import os
from datetime import date

st.title("🏆 Bülten & Analiz Paneli")

if not os.path.exists("all_leagues_data.csv"):
    st.error("Veri dosyası bulunamadı!")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # --- 1. KUTUCUK: TARİH ---
    st.info("📅 Tarih Seçimi")
    secilen_tarih = st.date_input("Bülten günü seçin:", date.today())

    # --- 2. KUTUCUK: LİG ---
    st.info("🌍 Lig Seçimi")
    ligler = sorted(df['League'].unique()) if 'League' in df.columns else ["Premier League"]
    secilen_lig = st.selectbox("Lig:", ligler)

    # --- 3. KUTUCUK: KARŞILAŞMA ---
    st.info("🏟️ Karşılaşma (Bülten)")
    # Seçilen tarih ve ligdeki maçları filtrele
    gunun_maclari = df[(df['Date'].dt.date == secilen_tarih)] # Lig filtresi de eklenebilir
    
    if not gunun_maclari.empty:
        mac_listesi = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
        secilen_mac = st.selectbox("Günün Maçları:", mac_listesi)
        
        # Seçilen maçın takımlarını ayır
        ev_takim = secilen_mac.split(" - ")[0]
        dep_takim = secilen_mac.split(" - ")[1]
        
        # --- 4. EN ALT: ALGORİTMALAR ---
        st.divider()
        st.subheader("🧠 Oran Algoritma Analizi")
        
        # Takımların geçmiş verilerine bakarak algoritma çalıştır
        gecmis_ev = df[(df['HomeTeam'] == ev_takim) | (df['AwayTeam'] == ev_takim)].tail(10)
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric(f"{ev_takim} Form (Son 10)", f"%{len(gecmis_ev[gecmis_ev['FTHG'] > 0]) * 10}")
        with c2:
            st.metric("İY 0.5 Üst Olasılığı", "%82") # Örnek algoritma çıktısı
            
    else:
        st.warning("Seçilen tarihte bu lig için bülten maçı bulunamadı.")
