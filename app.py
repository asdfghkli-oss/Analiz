import streamlit as st
import sqlite3
import pandas as pd
from collections import Counter

st.set_page_config(page_title="AI 5 Sezon Analiz", layout="wide")

# Görseldeki gibi Premium Kart Tasarımı
st.markdown("""
    <style>
    .stSelectbox, .stDateInput { color: white; }
    .card { padding: 15px; border-radius: 12px; margin: 8px; text-align: center; font-weight: bold; font-family: sans-serif; }
    .green { background-color: #BBF7D0; border: 1px solid #16A34A; color: #14532D; }
    .blue { background-color: #DBEafe; border: 1px solid #2563EB; color: #1E3A8A; }
    .purple { background-color: #E9D5FF; border: 1px solid #7C3AED; color: #4C1D95; }
    .yellow { background-color: #FEF08A; border: 1px solid #CA8A04; color: #713F12; }
    </style>
    """, unsafe_allow_html=True)

def query_db(sql):
    with sqlite3.connect("football.db") as conn:
        return pd.read_sql_query(sql, conn)

# --- ÜST FİLTRE PANELİ (İSTEDİĞİN TÜM SEÇENEKLER) ---
st.title("🏟️ 5 Yıllık Hafta & Periyot Analizörü")

# 1. Satır: Tarih, Lig, Takım
c1, c2, c3 = st.columns(3)
with c1:
    tarih = st.date_input("📅 Tarih Seç", value=pd.to_datetime("2026-04-03"))
with c2:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")['league'].tolist()
    secilen_lig = st.selectbox("🏆 Lig Seçin", ligler)
with c3:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")['home_team'].tolist()
    secilen_takim = st.selectbox("⚽ Takım Seçin", takimlar)

# 2. Satır: Sezon, Hafta, Algoritma
c4, c5, c6 = st.columns(3)
with c4:
    sezonlar = query_db("SELECT DISTINCT season FROM matches ORDER BY season DESC")['season'].tolist()
    secilen_sezon = st.selectbox("📅 Sezon (Başlangıç)", sezonlar)
with c5:
    hafta = st.number_input("🔢 Hafta (Döngü)", 1, 45, 30)
with c6:
    algoritma = st.selectbox("🧠 Algoritma Tipi", ["İY/MS Analizi", "ALT/ÜST Analizi", "İY/MS KG Analizi"])

# --- 5 SEZONLUK DERİN ANALİZ MOTORU ---
# Seçilen sezon ve öncesindeki 5 sezonu kapsar
sql_query = f"""
    SELECT home_score, away_score, ht_home_score, ht_away_score, league, season, week 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND week = {hafta}
    AND season <= '{secilen_sezon}'
    ORDER BY season DESC LIMIT 100
"""
df_analiz = query_db(sql_query)

if not df_analiz.empty:
    # Veri İşleme
    ms_skorlar = [f"{r['home_score']}-{r['away_score']}" for _, r in df_analiz.iterrows()]
    iy_skorlar = [f"{r['ht_home_score']}-{r['ht_away_score']}" for _, r in df_analiz.iterrows()]
    ms_goller = [f"{int(r['home_score'] + r['away_score'])} Gol" for _, r in df_analiz.iterrows()]
    iy_goller = [f"{int(r['ht_home_score'] + r['ht_away_score'])} Gol" for _, r in df_analiz.iterrows()]

    def render_stat_cards(liste, renk, baslik, ikon):
        st.markdown(f"#### {ikon} {baslik}")
        counts = Counter(liste)
        total = len(liste)
        top = counts.most_common(6)
        
        col_a, col_b = st.columns(2)
        for i, (val, count) in enumerate(top):
            yüzde = int((count/total)*100)
            html = f'<div class="card {renk}">{val} ({yüzde}%) {count} kere</div>'
            if i % 2 == 0: col_a.markdown(html, unsafe_allow_html=True)
            else: col_b.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    
    # GÖRSELDEKİ 4'LÜ KART YAPISI
    row1_1, row1_2 = st.columns(2)
    with row1_1:
        render_stat_cards(ms_skorlar, "green", "Maç Skoru Tahminleri", "🏟️")
    with row1_2:
        render_stat_cards(iy_skorlar, "blue", "İlk Yarı Skoru Tahminleri", "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)
    
    row2_1, row2_2 = st.columns(2)
    with row2_1:
        render_stat_cards(ms_goller, "purple", "Maç Sonu Gol Sayısı", "🌟")
    with row2_2:
        render_stat_cards(iy_goller, "yellow", "İlk Yarı Gol Sayısı", "⚽")

else:
    st.warning(f"⚠️ {secilen_takim} için {hafta}. haftada son 5 sezona ait veri bulunamadı.")
