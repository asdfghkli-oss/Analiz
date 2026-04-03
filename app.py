import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu", layout="centered")

# --- VERİTABANI ---
def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

# --- CSS: KUTUCUK İÇİ OK TASARIMI ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}

    /* ÖZEL KUTUCUK TASARIMI */
    .custom-selector {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 5px;
        height: 50px;
        border: 1px solid #ddd;
    }

    /* Görünmez Streamlit Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Analiz Listesi Belirginleştirme */
    .analysis-container {
        border: 1px solid #eee;
        border-radius: 12px;
        margin-top: 15px;
        background: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .match-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ÇEKME ---
ligler_df = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
ligler = ligler_df['league'].tolist() if not ligler_df.empty else []

# Lig ve Hafta
c1, c2 = st.columns([3, 1])
with c1:
    secilen_lig = st.selectbox("🏆 LİG", ligler)
with c2:
    hafta = st.number_input("🔢 HT", 1, 45, 30)

# Takım Listesi
takimlar_df = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}' ORDER BY home_team")
takimlar = takimlar_df['home_team'].tolist() if not takimlar_df.empty else []

if 't_idx' not in st.session_state: st.session_state.t_idx = 0

st.write("⚽ **TAKIM SEÇİMİ**")

# --- KUTUCUK İÇİ OK SİSTEMİ ---
# Tek bir satırda butonlar ve kutucuğu birleştiriyoruz
col_l, col_m, col_r = st.columns([1, 6, 1])

with col_l:
    if st.button("❮", key="p_btn", use_container_width=True):
        st.session_state.t_idx = (st.session_state.t_idx - 1) % len(takimlar)
        st.rerun()

with col_m:
    # İndeks kontrolü
    if st.session_state.t_idx >= len(takimlar): st.session_state.t_idx = 0
    current_takim = st.selectbox("", takimlar, index=st.session_state.t_idx, label_visibility="collapsed")
    st.session_state.t_idx = takimlar.index(current_takim)

with col_r:
    if st.button("❯", key="n_btn", use_container_width=True):
        st.session_state.t_idx = (st.session_state.t_idx + 1) % len(takimlar)
        st.rerun()

# --- ANALİZ ---
sql = f"""
    SELECT season, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{current_takim}' OR away_team = '{current_takim}')
    AND round = {hafta}
    ORDER BY season DESC LIMIT 5
"""
df = query_db(sql)

def get_iyms(h1, a1, h2, a2):
    iy = "1" if h1 > a1 else ("2" if h1 < a1 else "0")
    ms = "1" if h2 > a2 else ("2" if h2 < a2 else "0")
    return f"{iy}/{ms}"

if not df.empty:
    st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        color = "#e63946" if iyms in ["1/2", "2/1"] else ("#f39c12" if iyms in ["1/0", "2/0"] else "#adb5bd")
        
        st.markdown(f"""
            <div class="match-row">
                <div style="font-size:11px; width:55px; color:gray;">{r['season']}</div>
                <div style="text-align:center; flex-grow:1;">
                    <div style="font-size:14px;">{r['home_team']} <b>{int(r['home_score'])}-{int(r['away_score'])}</b> {r['away_team']}</div>
                    <span style="font-size:10px; color:#999;">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</span>
                </div>
                <div style="background:{color}; color:white; padding:4px 8px; border-radius:5px; font-size:11px; font-weight:bold; width:45px; text-align:center;">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
