import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Mega Döngü Analiz", layout="wide")
st.title("🔄 5 Yıllık Hafta & Periyot Analizörü")

@st.cache_data
def veri_yukle():
    if os.path.exists("all_leagues_data.csv"):
        return pd.read_csv("all_leagues_data.csv")
    return None

df = veri_yukle()

if df is not None:
    st.sidebar.success(f"Sistemde {len(df)} maç kayıtlı.")
    
    # Filtreler
    with st.sidebar:
        st.header("🔍 Analiz Filtresi")
        ulke_listesi = sorted(df['League'].unique())
        secilen_lig = st.selectbox("Lig Seç:", ulke_listesi)
        
        takimlar = sorted(df[df['League'] == secilen_lig]['Home'].unique())
        secilen_takim = st.selectbox("Takım Seç:", takimlar)
        
        hafta = st.slider("Hangi Haftayı Analiz Edelim?", 1, 42, 30)

    # ANALİZ MOTORU
    # Takımın hem ev hem deplasman maçlarını, belirtilen haftada filtrele
    analiz_df = df[
        ((df['Home'] == secilen_takim) | (df['Away'] == secilen_takim)) & 
        (df['Wk'].astype(str) == str(hafta))
    ].sort_values(by="Season", ascending=False)

    st.subheader(f"📊 {secilen_takim} - {hafta}. Hafta Döngüsü (Son 5 Sezon)")
    
    if not analiz_df.empty:
        st.dataframe(analiz_df[['Season', 'League', 'Home', 'Score', 'Away']], use_container_width=True)
        
        # Basit İstatistik Çıkarımı
        st.info(f"💡 {secilen_takim} son 5 sezonda {hafta}. haftalarda toplam {len(analiz_df)} maç yaptı.")
    else:
        st.warning("Bu kriterlere uygun maç kaydı bulunamadı.")
else:
    st.error("Veri dosyası bulunamadı. Lütfen GitHub Actions'ı çalıştırın.")
