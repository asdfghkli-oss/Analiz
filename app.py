import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz Algoritması", layout="centered")

# CSS ile kutucuk tasarımlarını özelleştirme
st.markdown("""
    <style>
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if not os.path.exists("all_leagues_data.csv"):
    st.error("Veri dosyası bulunamadı. Lütfen GitHub Actions çalıştırın.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    st.title("🏆 Akıllı Tahmin Algoritması")

    # 1. KUTUCUK: TARİH SEÇİMİ
    st.subheader("📅 Tarih Aralığı")
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Analiz edilecek süreyi seçin:", [min_date, max_date])

    # 2. KUTUCUK: LİG SEÇİMİ
    st.subheader("🌍 Lig")
    ligler = sorted(df['League'].unique())
    secilen_lig = st.selectbox("Bir lig seçin:", ligler)

    # Veriyi filtrele
    mask = (df['League'] == secilen_lig) & (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    filtered_df = df[mask].copy()

    # 3. KUTUCUK: KARŞILAŞMA SEÇİMİ (TAKIM)
    st.subheader("🏟️ Karşılaşma Analizi")
    takimlar = sorted(pd.concat([filtered_df['HomeTeam'], filtered_df['AwayTeam']]).unique())
    secilen_takim = st.selectbox("Hangi takımın geçmiş verilerini getirelim?", takimlar)

    # Seçilen takıma göre maçları ayır
    t_df = filtered_df[(filtered_df['HomeTeam'] == secilen_takim) | (filtered_df['AwayTeam'] == secilen_takim)].copy()
    t_df['İY'] = t_df['HTHG'].astype(int).astype(str) + "-" + t_df['HTAG'].astype(int).astype(str)
    t_df['MS'] = t_df['FTHG'].astype(int).astype(str) + "-" + t_df['FTAG'].astype(int).astype(str)
    
    st.dataframe(t_df[['Date', 'HomeTeam', 'AwayTeam', 'İY', 'MS']].sort_values(by='Date', ascending=False), use_container_width=True)

    # 4. EN ALT: ORAN ALGORİTMALARI VE TAHMİN MOTORU
    st.divider()
    st.subheader("🧠 Oran & Yüzde Algoritmaları")
    
    if not t_df.empty:
        total_m = len(t_df)
        # Algoritma 1: 2.5 Üst Yüzdesi
        ust_count = len(t_df[(t_df['FTHG'] + t_df['FTAG']) > 2.5])
        ust_oran = (ust_count / total_m) * 100
        
        # Algoritma 2: KG Var Yüzdesi
        kg_count = len(t_df[(t_df['FTHG'] > 0) & (t_df['FTAG'] > 0)])
        kg_oran = (kg_count / total_m) * 100
        
        # Algoritma 3: İlk Yarı Gol Yüzdesi
        iy_gol_count = len(t_df[(t_df['HTHG'] + t_df['HTAG']) > 0])
        iy_gol_oran = (iy_gol_count / total_m) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("2.5 Üst İhtimali", f"%{round(ust_oran, 1)}")
        with col2:
            st.metric("KG Var İhtimali", f"%{round(kg_oran, 1)}")
        with col3:
            st.metric("İY 0.5 Üst İhtimali", f"%{round(iy_gol_oran, 1)}")
            
        # Skor Dağılım Algoritması
        st.info(f"💡 **Algoritma Notu:** {secilen_takim} son {total_m} maçında en çok **{t_df['MS'].value_counts().idxmax()}** skoruyla sahadan ayrıldı.")
    else:
        st.warning("Bu tarih aralığında seçili takımın maçı bulunamadı.")
