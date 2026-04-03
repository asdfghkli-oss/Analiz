import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Sayfa Genişliği ve Stil
st.set_page_config(page_title="Akıllı Analiz", layout="centered")

st.markdown("""
    <style>
    .stSelectbox { margin-bottom: 20px; }
    .reportview-container { background: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

if not os.path.exists("all_leagues_data.csv"):
    st.error("⚠️ Veri dosyası bulunamadı. Lütfen GitHub Actions üzerinden 'Run Workflow' yapın.")
else:
    # Veriyi oku ve tarih hatasını burada da engelle
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    st.title("🏟️ Akıllı Analiz Paneli")

    # --- 1. KUTUCUK: TARİH ---
    st.info("📅 1. ADIM: TARİH SEÇİMİ")
    # Bugünün tarihini varsayılan yap
    secilen_tarih = st.date_input("Analiz edilecek gün:", datetime.now().date())

    # --- 2. KUTUCUK: LİG ---
    st.info("🌍 2. ADIM: LİG SEÇİMİ")
    ligler = sorted(df['League'].unique())
    secilen_lig = st.selectbox("Lütfen bir lig seçin:", ligler)

    # --- 3. KUTUCUK: KARŞILAŞMA ---
    st.info("🤝 3. ADIM: KARŞILAŞMA SEÇİMİ")
    
    # Seçilen tarih ve ligdeki maçları filtrele
    mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
    gunun_df = df[mask].copy()
    
    if not gunun_df.empty:
        gunun_df['MatchName'] = gunun_df['HomeTeam'] + " - " + gunun_df['AwayTeam']
        secilen_mac = st.selectbox("Günün Bülteni:", gunun_df['MatchName'])
        
        # Seçilen maçın detaylarını al
        mac_detay = gunun_df[gunun_df['MatchName'] == secilen_mac].iloc[0]
        ev_takim = mac_detay['HomeTeam']
        dep_takim = mac_detay['AwayTeam']

        # --- 4. EN ALT: ORAN ALGORİTMALARI ---
        st.divider()
        st.subheader("🧠 Algoritma Analiz Sonuçları")
        
        # Geçmiş 10 maça bakarak algoritma çalıştır (Ev sahibi için)
        gecmis_ev = df[(df['HomeTeam'] == ev_takim) | (df['AwayTeam'] == ev_takim)].dropna(subset=['FTHG']).tail(10)
        
        if len(gecmis_ev) > 0:
            ust_sayisi = len(gecmis_ev[(gecmis_ev['FTHG'] + gecmis_ev['FTAG']) > 2.5])
            ust_ihtimal = (ust_sayisi / len(gecmis_ev)) * 100
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("2.5 Üst Olasılığı", f"%{round(ust_ihtimal, 1)}")
            with c2:
                # KG Var Algoritması
                kg_sayisi = len(gecmis_ev[(gecmis_ev['FTHG'] > 0) & (gecmis_ev['FTAG'] > 0)])
                kg_ihtimal = (kg_sayisi / len(gecmis_ev)) * 100
                st.metric("KG Var Olasılığı", f"%{round(kg_ihtimal, 1)}")
            
            st.success(f"💡 Not: {ev_takim} son 10 maçının {ust_sayisi} tanesini 2.5 Üst bitirdi.")
        else:
            st.warning("Bu karşılaşma için yeterli arşiv verisi bulunamadı.")
            
    else:
        st.warning(f"Seçilen tarihte ({secilen_tarih}) {secilen_lig} bülteni bulunamadı.")
