import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu Pro", layout="centered")

# --- VERİTABANI ---
def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

# --- TEMA & STİL (Kutucuk ve Oklar İçin Özel Tasarım) ---
if 'theme' not in st.session_state: st.session_state.theme = 'Light'

st.markdown(f"""
    <style>
    .stApp {{ background-color: {'#ffffff' if st.session_state.theme == 'Light' else '#17212b'}; }}
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 1.5rem;}}
    
    /* Butonları Hizala */
    div.stButton > button {{
        width: 100%;
        height: 45px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background-color: transparent;
        font-weight: bold;
    }}

    /* Analiz Tablosu */
    .analysis-container {{
        background-color: {'#ffffff' if st.session_state.theme == 'Light' else '#1e2c3a'};
        border-radius: 12px;
        padding: 5px;
        border: 1px solid {'#eeeeee' if st.session_state.theme == 'Light' else '#2b3948'};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    .match-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 10px;
        border-bottom: 1px solid {'#f1f1f1' if st.session_state.theme == 'Light' else '#2b3948'};
        color: {'#212529' if st.session_state.theme == 'Light' else '#ffffff'};
    }}
    
    .ms-val {{ font-size: 17px; font-weight: 800; }}
    .iy-val {{ font-size: 11px; color: #888; display: block; margin-top: -2px; }}
    
    .badge {{
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        width: 50px;
        text-align: center;
    }}
    .bg-supriz {{ background-color: #ff0000 !important; color: white !important; }}
    .bg-draw {{ background-color: #f39c12 !important; color: white !important; }}
    .bg-normal {{ background-color: #dee2e6 !important; color: #495057 !important; }}
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.session_state.theme = st.radio("Görünüm", ['Light', 'Dark'])

# --- 1. LİG VE HAFTA ---
ligler_df = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
ligler = ligler_df['league'].tolist() if not ligler_df.empty else []

c_lig, c_hafta = st.columns([2, 1])
with c_lig:
    secilen_lig = st.selectbox("🏆 LİG", ligler)
with c_hafta:
    hafta = st.number_input("🔢 HAFTA", 1, 45, 30)

# --- 2. TAKIM SEÇİMİ (TEK SATIRDA OKLAR VE KUTUCUK) ---
takimlar_df = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}' ORDER BY home_team")
takimlar = takimlar_df['home_team'].tolist() if not takimlar_df.empty else []

if 't_idx' not in st.session_state: st.session_state.t_idx = 0

st.write("⚽ **TAKIM**")
# [Ok] [Kutucuk] [Ok] Düzeni
col_left, col_mid, col_right = st.columns([1, 6, 1])

with col_left:
    if st.button("<", key="prev"):
        st.session_state.t_idx = (st.session_state.t_idx - 1) % len(takimlar)
        st.rerun()

with col_right:
    if st.button(">", key="next"):
        st.session_state.t_idx = (st.session_state.t_idx + 1) % len(takimlar)
        st.rerun()

with col_mid:
    # Kutucuk ok tuşlarıyla senkronize çalışır
    current_takim = st.selectbox("Takim_Box", takimlar, index=st.session_state.t_idx, label_visibility="collapsed")
    st.session_state.t_idx = takimlar.index(current_takim)

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
    st.warning(f"🤖 {current_takim} için {hafta}. haftada geçmiş veri bulunamadı.")
