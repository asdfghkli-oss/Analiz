import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="FBref Analiz", layout="wide")
st.title("⚽ FBref Canlı Maç Listesi")

# Dosya kontrolü
if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    
    # Sütun isimlerini temizle (boşluk varsa siler)
    df.columns = df.columns.str.strip()

    # --- ESNEK FİLTRELEME ---
    # Eğer lig verisi varsa göster
    if 'League' in df.columns and not df.empty:
        ligler = sorted(df['League'].dropna().unique().tolist())
        
        c1, c2 = st.columns(2)
        with c1:
            secilen_lig = st.selectbox("🌍 Lig Seçin:", ["Hepsi"] + ligler)
        with c2:
            st.info(f"📊 Toplam {len(df)} maç yüklendi.")

        # Filtreleme Uygula
        if secilen_lig != "Hepsi":
            gunun_maclari = df[df['League'] == secilen_lig].copy()
        else:
            gunun_maclari = df.copy()

        if not gunun_maclari.empty:
            # Maçları birleştirip göster
            gunun_maclari['Match'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
            
            # Tablo olarak göster (Tarih hatası olsa bile burada liste çıkar)
            st.dataframe(gunun_maclari[['Date', 'League', 'Match']], use_container_width=True)
            
            secilen_mac = st.selectbox("🏟️ Detaylı Analiz İçin Seç:", gunun_maclari['Match'])
            st.success(f"🔍 {secilen_mac} seçildi. Analiz motoru çalışıyor...")
        else:
            st.warning("Seçilen ligde maç bulunamadı.")
    else:
        st.error("Dosya bulundu ama içinde maç verisi yok.")
else:
    st.error("📂 Veri dosyası (CSV) henüz oluşturulmamış.")
