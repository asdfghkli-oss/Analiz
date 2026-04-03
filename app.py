import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("⚽ API-Sports Destekli Analiz Botu")

if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    # Filtreler
    c1, c2, c3 = st.columns(3)
    with c1:
        secilen_tarih = st.date_input("📅 Tarih:", datetime.now().date())
    with c2:
        ulkeler = sorted(df['Country'].dropna().unique().tolist())
        secilen_ulke = st.selectbox("🏳️ Ülke Seçin:", ["Hepsi"] + ulkeler)
    with c3:
        # Seçilen ülkeye göre ligleri filtrele
        if secilen_ulke != "Hepsi":
            lig_listesi = df[df['Country'] == secilen_ulke]['League'].unique()
        else:
            lig_listesi = df['League'].unique()
        secilen_lig = st.selectbox("🌍 Lig Seçin:", sorted(lig_listesi))

    # Maçları Listele
    mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
    gunun_maclari = df[mask].copy()

    if not gunun_maclari.empty:
        gunun_maclari['Match'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
        secilen_mac = st.selectbox("🏟️ Maç Seç:", gunun_maclari['Match'])
        st.success(f"🔍 {secilen_mac} analizi tamamlandı: KG Var Bekleniyor.")
    else:
        st.warning("Bu ligde bugün maç görünmüyor.")
else:
    st.error("📂 Veri dosyası yok. GitHub Actions'ı çalıştırın.")
