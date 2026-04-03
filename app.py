import streamlit as st
import sqlite3
import pandas as pd
from collections import Counter

# Bot görünümü için daraltılmış düzen
st.set_page_config(page_title="Analiz Botu", layout="centered")

# Telegram Botu CSS Tasarımı
st.markdown("""
    <style>
    .stApp { background-color: #1c2733; }
    .bot-header { color: #5dade2; text-align: center; font-family: sans-serif; margin-bottom: 20px; }
    .result-card {
        background-color: #24303f;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #3d4b59;
        margin-bottom: 15px;
    }
    .score-pill {
        display: inline-block;
        width: 100%;
        margin: 4px 0;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        color: #1a1a1a;
    }
    .green { background-color: #a7f3d0; border-left: 5px solid #059669; }
    .blue { background-color: #bfdbfe; border-left: 5px solid #2563eb; }
    .purple { background-color: #ddd6fe; border-left: 5px solid #7c3aed; }
    .yellow { background-color: #fef08a; border-left: 5px solid #ca8a04; }
    label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

def get_data(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

st.markdown("<h2 class='bot-header'>📊 SKOR ANALİZ BOTU</h2>", unsafe_allow_html=True)

# --- BOT GİRİŞ ALANLARI ---
col1, col2 = st.columns(2)
with col1:
    ligler = get_data("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig", ligler['league'].tolist() if not ligler.empty else [])
with col2:
    takimlar = get_data(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım", takimlar['home_team'].tolist() if not takimlar.empty else [])

hafta = st.number_input("🔢 Analiz Haftası (Round)", 1, 45, 30)

# --- BOT HIZLI ANALİZ MOTORU ---
# Sütun adı 'round' olarak güncellendi, son 5 sezonu kapsar.
sql_query = f"""
    SELECT home_score, away_score, ht_home_score, ht_away_score, season 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC
"""
df = get_data(sql_query)

if not df.empty:
    st.markdown(f"<p style='color:gray; text-align:center;'>Son {len(df)} sezonun {hafta}. hafta verileri analiz edildi.</p>", unsafe_allow_html=True)
    
    # Veri İşleme
    ms_skorlar = [f"{int(r['home_score'])}-{int(r['away_score'])}" for _, r in df.iterrows()]
    iy_skorlar = [f"{int(r['ht_home_score'])}-{int(r['ht_away_score'])}" for _, r in df.iterrows()]
    ms_goller = [f"{int(r['home_score'] + r['away_score'])} Gol" for _, r in df.iterrows()]
    iy_goller = [f"{int(r['ht_home_score'] + r['ht_away_score'])} Gol" for _, r in df.iterrows()]

    def render_bot_section(title, data_list, color_class):
        st.markdown(f"<h4 style='color:white; margin-top:20px;'>{title}</h4>", unsafe_allow_html=True)
        counts = Counter(data_list)
        total = len(data_list)
        for val, count in counts.most_common(5):
            perc = int((count/total)*100)
            st.markdown(f'<div class="score-pill {color_class}">{val} &nbsp; | &nbsp; %{perc} ({count} Maç)</div>', unsafe_allow_html=True)

    # Bot Yanıtları (Alt alta hızlı liste)
    render_bot_section("🏠 Maç Skoru Tahminleri", ms_skorlar, "green")
    render_bot_section("⏱️ İlk Yarı Skoru Tahminleri", iy_skorlar, "blue")
    render_bot_section("🌟 Maç Sonu Toplam Gol", ms_goller, "purple")
    render_bot_section("⚽ İlk Yarı Toplam Gol", iy_goller, "yellow")

else:
    st.error("🤖 Bot bu takım için o haftaya ait geçmiş veri bulamadı.")

