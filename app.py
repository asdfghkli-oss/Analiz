import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pro Bülten Analiz", layout="centered")

# Görsel Stil Ayarları
st.markdown("<style>.stSelectbox {margin-bottom: 15px;}</style>", unsafe_allow_html=True)

if not os.path.exists("all_leagues_data.csv"):
    st.error("⚠️ Veri dosyası bulunamadı! GitHub Actions'ı çalıştırın.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    st.title("⚽ Akıllı Analiz Paneli")

    # --- 1. KUTUCUK: TARİH ---
    st.subheader("📅 1. Analiz Tarihi")
    secilen_tarih = st.date_input("Hangi günün bültenine bakalım?", datetime.now().date())

    # --- 2. KUTUCUK: LİG ---
    st.subheader("🌍 2. Lig")
    ligler = sorted(df['League'].unique())
    secilen_lig = st.selectbox("Bir lig seçiniz:", ligler)

    # --- 3. KUTUCUK: KARŞILAŞMA ---
    st.subheader("🏟️ 3. Karşılaşma")
    mask = (df['Date'].dt.date == secilen_tarih) & (df['League'] == secilen_lig)
    gunun_maclari = df[mask].copy()

    if not gunun_maclari.empty:
        gunun_maclari['Match'] = gunun_maclari['HomeTeam'] + " - " + gunun_maclari['AwayTeam']
        secilen_mac = st.selectbox("Günün Maç Listesi:", gunun_maclari['Match'])
        
        # Takım detaylarını al
        mac_verisi = gunun_maclari[gunun_maclari['Match'] == secilen_mac].iloc[0]
        ev = mac_verisi['HomeTeam']
        dep = mac_verisi['AwayTeam']

        # --- 4. EN ALT: ALGORİTMALAR ---
        st.divider()
        st.subheader("🧠 Oran & İstatistik Algoritması")
        
        # Seçilen takımların ARŞİV verilerine bak (Oynanmış son 10 maç)
        arsiv = df.dropna(subset=['FTHG'])
        ev_gecmis = arsiv[(arsiv['HomeTeam'] == ev) | (arsiv['AwayTeam'] == ev)].tail(10)
        
        if not ev_gecmis.empty:
            # Algoritma 1: 2.5 Üst Yüzdesi
            ust_yuzde = (len(ev_gecmis[(ev_gecmis['FTHG'] + ev_gecmis['FTAG']) > 2.5]) / len(ev_gecmis)) * 100
            # Algoritma 2: Karşılıklı Gol Yüzdesi
            kg_yuzde = (len(ev_gecmis[(ev_gecmis['FTHG'] > 0) & (ev_gecmis['FTAG'] > 0)]) / len(ev_gecmis)) * 100
            
            c1, c2 = st.columns(2)
            c1.metric("2.5 Üst Olasılığı", f"%{round(ust_yuzde, 1)}")
            c2.metric("KG Var Olasılığı", f"%{round(kg_yuzde, 1)}")
            
            st.success(f"💡 **Algoritma Notu:** {ev} takımı son 10 maçında %{int(ust_yuzde)} oranında 2.5 Üst barajını aştı.")
        else:
            st.warning("Bu maç için yeterli geçmiş veri (arşiv) bulunamadı.")
            
    else:
        st.warning(f"Seçilen tarihte ({secilen_tarih}) {secilen_lig} bülteni henüz yüklenmemiş.")

# Alt Bilgi
st.caption("Veriler FixtureDownload üzerinden anlık olarak güncellenmektedir.")
