import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Analiz Botu", layout="centered")

# Telegram Sistem Teması ve Tek Satır Maç Görünümü (CSS)
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #17212b; }
    
    /* Seçim Kutuları Düzenleme */
    .stSelectbox div, .stNumberInput div { 
        background-color: #242f3d !important; 
        color: white !important; 
        border-radius: 10px !important;
    }
    
    /* Tek Satır Maç Kartı */
    .match-row {
        background-color: #242f3d;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #5288c1;
        color: #f5f5f5;
        font-family: 'Roboto', sans-serif;
    }
    
    .season-tag { color: #6ab3f3; font-size: 12px; font-weight: bold; width: 60px; }
    .teams-text { flex-grow: 1; text-align: center; font-size: 14px; }
    .score-badge { 
        background-color: #1c2733; 
        padding: 2px 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        color: #ffca28;
        margin: 0 10px;
    }
    .iyms-tag { 
        background-color: #3d4b59; 
        color: #e0e0e0; 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-size: 11px; 
        width: 50px;
        text-align: center;
    }
    
    h2, h4, label { color: #5288c1 !important; }
    hr { border-top: 1px solid #2b3948; }
    </style>
    """, unsafe_allow_html=True)

def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

def get_iyms(h1, a1, h2, a2):
    iy = "1" if h1 > a1 else ("2" if h1 < a1 else "0")
    ms = "1" if h2 > a2 else ("2" if h2 < a2 else "0")
    return f"{iy}/{ms}"

st.markdown("<h2 style='text-align:center;'>📊 ANALİZ BOTU</h2>", unsafe_allow_html=True)

# --- ÜST SEÇİM ALANI ---
c1, c2 = st.columns(2)
with c1:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig", ligler['league'].tolist() if not ligler.empty else [])
with c2:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım", takimlar['home_team'].tolist() if not takimlar.empty else [])

hafta = st.number_input("🔢 Hafta (Round)", 1, 45, 30)

st.markdown("---")

# --- VERİ SORGUSU ---
sql = f"""
    SELECT season, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC LIMIT 5
"""
df = query_db(sql)

if not df.empty:
    st.markdown(f"<p style='color:#6ab3f3; font-size:13px;'>{secilen_takim} - Son 5 Sezon ({hafta}. Hafta)</p>", unsafe_allow_html=True)
    
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        # Tek Satır Tasarımı
        st.markdown(f"""
            <div class="match-row">
                <div class="season-tag">{r['season']}</div>
                <div class="teams-text">
                    {r['home_team']} <span class="score-badge">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}
                </div>
                <div class="iyms-tag">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("🤖 Bu kriterlere uygun geçmiş maç kaydı bulunamadı.")
