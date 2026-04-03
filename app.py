import streamlit as st
import sqlite3
import pandas as pd
from collections import Counter

st.set_page_config(page_title="AI Döngü Analizörü", layout="wide")

# Modern Kart Tasarımı (CSS)
st.markdown("""
    <style>
    .card { padding: 15px; border-radius: 12px; margin: 8px; text-align: center; font-weight: bold; }
    .green { background-color: #BBF7D0; border: 1px solid #16A34A; color: #14532D; }
    .blue { background-color: #DBEafe; border: 1px solid #2563EB; color: #1E3A8A; }
    .purple { background-color: #E9D5FF; border: 1px solid #7C3AED; color: #4C1D95; }
    .yellow { background-color: #FEF08A; border: 1px solid #CA8A04; color: #713F12; }
    </style>
    """, unsafe_allow_html=True)

def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except Exception as e:
        st.error(f"Veritabanı Hatası: {e}")
        return pd.DataFrame()

st.title("🏟️ 5 Yıllık Periyot Analizörü")

# --- ÜST PANEL (SEZON SİLİNDİ) ---
row1_c1, row1_c2, row1_c3 = st.columns(3)
with row1_c1:
    tarih = st.date_input("📅 Tarih Seç", value=pd.to_datetime("2026-04-03"))
with row1_c2:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig Seçin", ligler['league'].tolist() if not ligler.empty else [])
with row1_c3:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım Seçin", takimlar['home_team'].tolist() if not takimlar.empty else [])

row2_c1, row2_c2 = st.columns(2)
with row2_c1:
    hafta = st.number_input("🔢 Hafta (Döngü)", 1, 45, 30)
with row2_c2:
    algoritma = st.selectbox("🧠 Algoritma", ["İY/MS Analizi", "ALT/ÜST Analizi", "İY/MS KG Analizi"])

# --- OTOMATİK 5 SEZON ANALİZ MOTORU ---
# Sezon seçimi olmadığı için mevcut tarihten geriye dönük tüm yılları tarar
sql_query = f"""
    SELECT home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND week = {hafta}
    ORDER BY season DESC
"""
df_analiz = query_db(sql_query)

if not df_analiz.empty:
    # Veri Hazırlama
    ms_skorlar = [f"{int(r['home_score'])}-{int(r['away_score'])}" for _, r in df_analiz.iterrows()]
    iy_skorlar = [f"{int(r['ht_home_score'])}-{int(r['ht_away_score'])}" for _, r in df_analiz.iterrows()]
    ms_goller = [f"{int(r['home_score'] + r['away_score'])} Gol" for _, r in df_analiz.iterrows()]
    iy_goller = [f"{int(r['ht_home_score'] + r['ht_away_score'])} Gol" for _, r in df_analiz.iterrows()]

    def render_cards(data, color, title, icon):
        st.markdown(f"#### {icon} {title}")
        counts = Counter(data)
        total = len(data)
        top_6 = counts.most_common(6)
        
        c_left, c_right = st.columns(2)
        for i, (val, count) in enumerate(top_6):
            perc = int((count/total)*100)
            html = f'<div class="card {color}">{val} ({perc}%) {count} kere</div>'
            if i % 2 == 0: c_left.markdown(html, unsafe_allow_html=True)
            else: c_right.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    
    # 4'LÜ KART GÖRÜNÜMÜ
    r1, r2 = st.columns(2)
    with r1:
        render_cards(ms_skorlar, "green", "Maç Skoru Tahminleri", "🏟️")
    with r2:
        render_cards(iy_skorlar, "blue", "İlk Yarı Skoru Tahminleri", "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)
    
    r3, r4 = st.columns(2)
    with r3:
        render_cards(ms_goller, "purple", "Maç Sonu Gol Sayısı", "🌟")
    with r4:
        render_cards(iy_goller, "yellow", "İlk Yarı Gol Sayısı", "⚽")
else:
    st.info(f"💡 {secilen_takim} için {hafta}. haftaya ait geçmiş veri bulunamadı.")
