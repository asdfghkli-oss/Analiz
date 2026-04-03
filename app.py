import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Analiz Botu Pro", layout="centered")

# --- VERİTABANI ---
def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

# --- TEMA & STİL ---
if 'theme' not in st.session_state: st.session_state.theme = 'Light'

st.markdown(f"""
    <style>
    .stApp {{ background-color: {'#ffffff' if st.session_state.theme == 'Light' else '#17212b'}; }}
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 1rem;}}

    /* OKLARI VE KUTUCUĞU YAN YANA ZORLA */
    [data-testid="column"] {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    /* Mobilde sütunların alt alta binmesini engelle */
    [data-testid="stHorizontalBlock"] {{
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }}

    .stButton button {{
        width: 100% !important;
        padding: 0px !important;
        height: 42px !important;
        border-radius: 8px !important;
    }}

    .analysis-container {{
        background-color: {'#ffffff' if st.session_state.theme == 'Light' else '#1e2c3a'};
        border-radius: 12px;
        padding: 5px;
        border: 1px solid {'#eeeeee' if st.session_state.theme == 'Light' else '#2b3948'};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 10px;
    }}
    
    .match-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 10px;
        border-bottom: 1px solid {'#f1f1f1' if st.session_state.theme == 'Light' else '#2b3948'};
        color: {'#212529' if st.session_state.theme == 'Light' else '#ffffff'};
    }}
    
    .ms-val {{ font-size: 16px; font-weight: 800; }}
    .iy-val {{ font-size: 10px; color: #888; display: block; }}
    
    .badge {{
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        width: 45px;
        text-align: center;
    }}
    .bg-supriz {{ background-color: #ff0000 !important; color: white !important; }}
    .bg-draw {{ background-color: #f39c12 !important; color: white !important; }}
    .bg-normal {{ background-color: #dee2e6 !important; color: #495057 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ÇEKME ---
ligler_df = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
ligler = ligler_df['league'].tolist() if not ligler_df.empty else []

# 1. LİG VE HAFTA SEÇİMİ
c1, c2 = st.columns([2, 1])
with c1:
    secilen_lig = st.selectbox("🏆 LİG", ligler)
with c2:
    hafta = st.number_input("🔢 HAFTA", 1, 45, 30)

# 2. TAKIM SEÇİMİ (MOBİL UYUMLU TEK SATIR)
takimlar_df = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}' ORDER BY home_team")
takimlar = takimlar_df['home_team'].tolist() if not takimlar_df.empty else []

if 't_idx' not in st.session_state: st.session_state.t_idx = 0

st.write("⚽ **TAKIM**")
# Sütunları genişliklerine göre zorla: Sol Ok (15%), Seçim (70%), Sağ Ok (15%)
col_l, col_m, col_r = st.columns([0.15, 0.7, 0.15])

with col_l:
    if st.button("<", key="b_prev"):
        st.session_state.t_idx = (st.session_state.t_idx - 1) % len(takimlar)
        st.rerun()

with col_m:
    # İndeksi kontrol et (Lig değişince hata vermemesi için)
    if st.session_state.t_idx >= len(takimlar): st.session_state.t_idx = 0
    current_takim = st.selectbox("T", takimlar, index=st.session_state.t_idx, label_visibility="collapsed")
    st.session_state.t_idx = takimlar.index(current_takim)

with col_r:
    if st.button(">", key="b_next"):
        st.session_state.t_idx = (st.session_state.t_idx + 1) % len(takimlar)
        st.rerun()

# --- ANALİZ MOTORU ---
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
        b_class = "bg-supriz" if iyms in ["1/2", "2/1"] else ("bg-draw" if iyms in ["1/0", "2/0"] else "bg-normal")
        
        st.markdown(f"""
            <div class="match-row">
                <div style="font-size:11px; width:55px; color:gray;">{r['season']}</div>
                <div style="text-align:center; flex-grow:1;">
                    <div style="font-size:14px;">{r['home_team']} <span class="ms-val">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}</div>
                    <span class="iy-val">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</span>
                </div>
                <div class="badge {b_class}">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning(f"🤖 {current_takim} için {hafta}. hafta verisi yok.")
