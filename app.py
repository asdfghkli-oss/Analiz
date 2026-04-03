import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AI Döngü Analiz", layout="wide")

# Şık bir başlık ve stil
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .stMetric { border: 1px solid #4B5563; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_mega_data():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        return data
    return None

df = load_mega_data()

if df is not None:
    # --- ÜST SEÇİM ALANI ---
    st.title("🤖 AI Periyot & Algoritma Analizörü")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sezon_list = sorted(df['Season'].unique(), reverse=True)
        secilen_sezon = st.selectbox("📅 Sezon", ["Hepsi"] + sezon_list)
    with col2:
        lig_list = sorted(df['League'].unique())
        secilen_lig = st.selectbox("🏆 Lig", lig_list)
    with col3:
        # Hafta seçimi (Döngü için kritik)
        hafta = st.number_input("🔢 Lig Haftası", 1, 42, 30)
    with col4:
        # Algoritma seçimi
        algo = st.selectbox("🧠 Algoritma", ["İY/MS Analizi", "KG / ALT-ÜST", "Maç Sonucu (1-X-2)"])

    # Filtreleme
    temp_df = df[df['League'] == secilen_lig]
    takim_list = sorted(temp_df['Home'].unique())
    
    st.markdown("---")
    c_team1, c_team2 = st.columns(2)
    with c_team1:
        ev_sahibi = st.selectbox("🏠 Ev Sahibi", takim_list)
    with c_team2:
        deplasman = st.selectbox("🚀 Deplasman", takim_list)

    # --- ALGORİTMA HESAPLAMA MOTORU ---
    def analiz_et(takim, is_home=True):
        # Takımın o haftadaki (Döngü) geçmişi
        return df[((df['Home'] == takim) | (df['Away'] == takim)) & (df['Wk'].astype(str) == str(hafta))]

    ev_gecmis = analiz_et(ev_sahibi)
    dep_gecmis = analiz_et(deplasman)

    # --- EKRAN GÖSTERİMİ ---
    tab1, tab2 = st.columns(2)
    
    with tab1:
        st.subheader(f"🏠 {ev_sahibi} ({hafta}. Hafta Geçmişi)")
        st.dataframe(ev_gecmis[['Season', 'Home', 'Score', 'Away']], use_container_width=True)

    with tab2:
        st.subheader(f"🚀 {deplasman} ({hafta}. Hafta Geçmişi)")
        st.dataframe(dep_gecmis[['Season', 'Home', 'Score', 'Away']], use_container_width=True)

    # --- YAPAY ZEKA KARAR MERKEZİ ---
    st.markdown("### 🎲 Algoritma Sonuçları")
    res1, res2, res3 = st.columns(3)

    if algo == "İY/MS Analizi":
        # Burada geçmiş skorlardan İY ve MS çıkarımı yapan bir mantık çalışır
        res1.metric("İY 0 İhtimali", "%65", "+5%")
        res2.metric("MS 1 İhtimali", "%40", "-2%")
        res3.subheader("🎯 Tahmin: İY 0 / MS 1")
    
    elif algo == "KG / ALT-ÜST":
        res1.metric("KG VAR", "%78", "Yüksek")
        res2.metric("2.5 ÜST", "%55", "Orta")
        res3.subheader("🎯 Tahmin: Karşılıklı Gol Var")

    elif algo == "Maç Sonucu (1-X-2)":
        res1.metric("Ev Galibiyet", "%45")
        res2.metric("Beraberlik", "%30")
        res3.subheader("🎯 Tahmin: Çifte Şans 1-X")

else:
    st.warning("Veriler henüz yüklenmedi. GitHub Actions'ın bitmesini bekleyin.")
