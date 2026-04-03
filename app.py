import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("⚽ Maç Analiz Sistemi")

# Dosya kontrolü
if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    # --- HATA ÖNLEYİCİ KONTROL ---
    # Eğer 'Country' sütunu yoksa, boş bir liste oluşturur ve hata vermez
    if 'Country' in df.columns:
        ulkeler = sorted(df['Country'].dropna().unique().tolist())
    else:
        ulkeler = [] # Sütun yoksa hata verme, boş geç

    # Filtreler
    c1, c2 = st.columns(2)
    with c1:
        secilen_tarih = st.date_input("📅 Tarih:", datetime.now().date())
    with c2:
        secilen_ulke = st.selectbox("🏳️ Ülke Seçin:", ["Hepsi"] + ulkeler)

    # Ligleri Seçilen Ülkeye Göre Filtrele
    if 'Country' in df.columns and secilen_ulke != "Hepsi":
        lig_listesi = df[df['Country'] == secilen_ulke]['League'].unique()
    else:
        lig_listesi = df['League'].unique() if 'League' in df.columns else []

    if len(lig_listesi) > 0:
        secilen_lig = st.selectbox("🌍 Lig Seçin:", sorted(lig_listesi))
        
        # Maçları Listele
        mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
        gunun_maclari = df[mask].copy()

        if not gunun_maclari.empty:
            gunun_maclari['Match'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
            st.selectbox("🏟️ Maç Seç:", gunun_maclari['Match'])
        else:
            st.warning("Bu seçimde maç bulunamadı.")
    else:
        st.error("Lig verisi henüz yüklenmemiş.")
else:
    st.error("📂 Veri dosyası bulunamadı. Lütfen GitHub Actions'ı çalıştırın.")
