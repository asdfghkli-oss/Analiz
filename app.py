import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Football Analyzer", layout="wide")
st.title("⚽ Profesyonel Lig Analiz Arşivi")

if not os.path.exists("all_leagues_data.csv"):
    st.error("Veri dosyası bulunamadı. Lütfen Actions üzerinden veriyi çekin.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    
    # Tarih formatını bu kaynağa göre düzelt (dd/mm/yy)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    ligler = sorted(df['League'].unique())
    secilen_lig = st.sidebar.selectbox("Lig Seç", ligler)
    
    lig_df = df[df['League'] == secilen_lig].copy()
    
    # En güncel maçları (Bülten niyetine) ve geçmişi göster
    st.subheader(f"📊 {secilen_lig} Sonuçları ve Analiz")
    
    # Skoru olan (oynanmış) maçları göster
    played = lig_df.dropna(subset=['FTHG', 'FTAG'])
    played['Score'] = played['FTHG'].astype(int).astype(str) + " - " + played['FTAG'].astype(int).astype(str)
    
    st.dataframe(played[['Date', 'HomeTeam', 'AwayTeam', 'Score']].sort_values(by='Date', ascending=False))
    
    # İstatistik: En çok biten skor
    if not played.empty:
        common_score = played['Score'].value_counts().idxmax()
        st.success(f"💡 Bu ligde bu sezon en sık görülen skor: **{common_score}**")
