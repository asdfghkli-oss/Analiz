import streamlit as st
import sqlite3
import pandas as pd

# Bot görünümü için dar ekran ayarı
st.set_page_config(page_title="Analiz Botu", layout="centered")

# Telegram Botu Tasarımı (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #1c2733; }
    .bot-header { color: #5dade2; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .match-card {
        background-color: #24303f;
        padding: 12px;
        border-radius: 12px;
        border-left: 5px solid #5dade2;
        margin-bottom: 10px;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .score-text { font-size: 18px; font-weight: bold; color: #f1c40f; }
    .iyms-badge {
        background-color: #34495e;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 13px;
        color: #ecf0f1;
        float: right;
    }
    .date-text { color: #bdc3c7; font-size: 12px; }
    label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

# İY/MS Hesaplama Fonksiyonu
def get_iyms(h1, a1, h2, a2):
    # İY sonucu
    if h1 > a1: iy = "1"
    elif h1 < a1: iy = "2"
    else: iy = "0"
    # MS sonucu
    if h2 > a2: ms = "1"
    elif h2 < a2: ms = "2"
    else: ms = "0"
    return f"{iy}/{ms}"

st.markdown("<h2 class='bot-header'>🤖 MAÇ GEÇMİŞİ BOTU</h2>", unsafe_allow_html=True)

# --- SEÇİM ALANI ---
col1, col2 = st.columns(2)
with col1:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig", ligler['league'].tolist() if not ligler.empty else [])
with col2:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım", takimlar['home_team'].tolist() if not takimlar.empty else [])

hafta = st.number_input("🔢 Hafta (Round)", 1, 45, 30)

st.markdown("---")

# --- SON 5 SEZON SORGUSU ---
# 'round' sütunu üzerinden o haftanın geçmiş 5-6 sezonluk maçlarını getirir
sql = f"""
    SELECT season, date, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC
"""
df = query_db(sql)

if not df.empty:
    st.markdown(f"<p style='color:#bdc3c7; text-align:center;'>{secilen_takim} - {hafta}. Hafta Geçmişi</p>", unsafe_allow_html=True)
    
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        # Telegram Mesaj Kartı Tasarımı
        st.markdown(f"""
            <div class="match-card">
                <span class="date-text">{r['season']} | {r['date']}</span>
                <span class="iyms-badge">İY/MS: {iyms}</span>
                <div style="margin-top: 8px;">
                    <span style="font-size:15px;">{r['home_team']}</span> 
                    <span class="score-text"> {int(r['home_score'])} - {int(r['away_score'])} </span> 
                    <span style="font-size:15px;">{r['away_team']}</span>
                </div>
                <div style="font-size:12px; color:#95a5a6; margin-top:5px;">
                    İlk Yarı: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("🤖 Bu hafta için geçmiş maç kaydı bulunamadı.")
