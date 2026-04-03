import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Tahmin Algoritması", layout="centered")

# Dosya kontrolü
if not os.path.exists("all_leagues_data.csv"):
    st.error("⚠️ Veri dosyası (all_leagues_data.csv) GitHub'da henüz oluşmamış.")
    st.info("Lütfen GitHub'da Actions sekmesine gidip 'Run workflow' butonuna basın.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    st.title("⚽ Profesyonel Analiz Sistemi")

    # --- 1. KUTUCUK: TARİH ---
    st.subheader("📅 1. Tarih Seçimi")
    secilen_tarih = st.date_input("Analiz günü:", datetime.now().date())

    # --- 2. KUTUCUK: LİG ---
    st.subheader("🌍 2. Lig Seçimi")
    lig_listesi = sorted(df['League'].unique()) if not df.empty else []
    
    if lig_listesi:
        secilen_lig = st.selectbox("Lig seçin:", lig_listesi)

        # --- 3. KUTUCUK: KARŞILAŞMA ---
        st.subheader("🏟️ 3. Karşılaşma")
        mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
        gunun_maclari = df[mask].copy()

        if not gunun_maclari.empty:
            gunun_maclari['Match'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
            secilen_mac = st.selectbox("Maç listesi:", gunun_maclari['Match'])
            
            mac_verisi = gunun_maclari[gunun_maclari['Match'] == secilen_mac].iloc[0]
            ev = mac_verisi['HomeTeam']
            dep = mac_verisi['AwayTeam']

            # --- 4. EN ALT: ALGORİTMALAR ---
            st.divider()
            st.subheader("🧠 Algoritma Sonuçları")
            
            # Arşivden geçmiş maçları çek (Oynanmış olanlar)
            arsiv = df.dropna(subset=['FTHG'])
            gecmis = arsiv[(arsiv['HomeTeam'] == ev) | (arsiv['AwayTeam'] == ev)].tail(10)
            
            if not gecmis.empty:
                ust_yuzde = (len(gecmis[(gecmis['FTHG'] + gecmis['FTAG']) > 2.5]) / len(gecmis)) * 100
                kg_yuzde = (len(gecmis[(gecmis['FTHG'] > 0) & (gecmis['FTAG'] > 0)]) / len(gecmis)) * 100
                
                c1, c2 = st.columns(2)
                c1.metric("2.5 Üst Olasılığı", f"%{round(ust_yuzde, 1)}")
                c2.metric("KG Var Olasılığı", f"%{round(kg_yuzde, 1)}")
                st.success(f"💡 Algoritma: {ev} son 10 maçında %{int(ust_yuzde)} oranında 2.5 Üst bitirdi.")
            else:
                st.warning("Bu maç için yeterli geçmiş veri bulunamadı.")
        else:
            st.warning("Seçilen tarihte bu lig için maç bulunamadı.")
    else:
        st.error("Dosya içinde hiç lig verisi bulunamadı. Lütfen update_data.py dosyasını kontrol edin.")
