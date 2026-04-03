import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu Pro", layout="centered")

# --- TEMA SEÇİCİ (SAĞ ÜST KÖŞE) ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

with st.sidebar:
    st.session_state.theme = st.radio("Sistem Teması", ['Light', 'Dark'])

# --- DİNAMİK CSS (TEMA VE SADELEŞTİRME) ---
if st.session_state.theme == 'Dark':
    bg_color = "#17212b"
    text_color = "#ffffff"
    row_bg = "#242f3d"
    border_color = "#2b3948"
    sub_text = "#95a5a6"
else:
    bg_color = "#ffffff"
    text_color = "#212529"
    row_bg = "#fdfdfd"
    border_color = "#eeeeee"
    sub_text = "#7f8c8d"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    
    /* Maç Satırı: Balon etkisi kaldırıldı, düz çizgi ve sade zemin eklendi */
    .match-row {{
        background-color: {row_bg};
        padding: 8px 10px;
        margin-bottom: 2px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid {border_color};
        color: {text_color};
        font-family: sans-serif;
    }}
    
    .season-tag {{ color: {sub_text}; font-size: 11px; font-weight: bold; width: 55px; }}
    
    .teams-container {{ flex-grow: 1; text-align: center; }}
    
    .ms-score {{ font-size: 16px; font-weight: bold; margin: 0 8px; }}
    
    .iy-score-sub {{ font-size: 10px; color: {sub_text}; margin-top: -2px; }}

    /* İY/MS ETİKETLERİ */
    .iyms-base {{
        padding: 3px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        width: 45px;
        text-align: center;
    }}

    .iyms-normal {{ background-color: #adb5bd; color: white; }}
    .iyms-supriz {{ background-color: #ff0000; color: white; font-weight: 900; }}
    .iyms-beraberlik {{ background-color: #f39c12; color: white; }}

    h2, label, p {{ color: {text_color} !important; }}
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

st.markdown(f"<h2 style='text-align:center;'>📊 ANALİZ BOTU</h2>", unsafe_allow_html=True)

# --- FİLTRELER ---
c1, c2 = st.columns(2)
with c1:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig", ligler['league'].tolist() if not ligler.empty else [])
with c2:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım", takimlar['home_team'].tolist() if not takimlar.empty else [])

hafta = st.number_input("🔢 Hafta (Round)", 1, 45, 30)

st.markdown("---")

# --- VERİ LİSTELEME ---
sql = f"""
    SELECT season, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC
"""
df = query_db(sql)

if not df.empty:
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        if iyms in ["1/2", "2/1"]: badge_class = "iyms-supriz"
        elif iyms in ["1/0", "2/0"]: badge_class = "iyms-beraberlik"
        else: badge_class = "iyms-normal"
        
        st.markdown(f"""
            <div class="match-row">
                <div class="season-tag">{r['season']}</div>
                <div class="teams-container">
                    <div>{r['home_team']} <span class="ms-score">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}</div>
                    <div class="iy-score-sub">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</div>
                </div>
                <div class="iyms-base {badge_class}">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("🤖 Bu kriterlere uygun maç kaydı bulunamadı.")
