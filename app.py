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

# --- CSS: SÜTUNLARIN ALT ALTA BİNMESİNİ ENGELLE ---
st.markdown("""
    <style>
    /* Üst barı ve boşlukları temizle */
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem; padding-bottom: 1rem;}

    /* MOBİLDE SÜTUNLARI YAN YANA TUT (ZORUNLU) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    
    /* Sütun genişliklerini sabitle */
    [data-testid="column"] {
        width: fit-content !important;
        flex: unset !important;
        min-width: unset !important;
    }

    /* Ok Butonları Stili */
    .stButton button {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }

    /* Analiz Satırları */
    .analysis-container {
        border: 1px solid #eee;
        border-radius: 12px;
        margin-top: 10px;
        background: white;
    }
    .match-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #f1f1f1;
    }
    .match-row:last-child { border-bottom: none; }
    
    /* Skor ve İY Etiketleri */
    .ms-val { font-size: 16px; font-weight: bold; }
    .iy-val { font-size: 10px; color: #888; display: block; }
    .badge {
        padding: 4px 6px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: bold;
        width: 45px;
        text-align: center;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ ÇEKME ---
ligler_df = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
ligler = ligler_df['league'].tolist() if not ligler_df.empty else []

# Lig ve Hafta (Tek Satırda)
c_l, c_h = st.columns([3, 1])
with c_l:
    secilen_lig = st.selectbox("🏆 LİG", ligler)
with c_h:
    hafta = st.number_input("🔢 HT", 1, 45, 30)

# Takım Listesi
takimlar_df = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}' ORDER BY home_team")
takimlar = takimlar_df['home_team'].tolist() if not takimlar_df.empty else []

if 't_idx' not in st.session_state: st.session_state.t_idx = 0

st.write("⚽ **TAKIM SEÇİMİ**")

# --- OKLAR VE KUTUCUK (MOBİLDE ASLA BOZULMAZ) ---
# Üç sütun: Sol Ok (Otomatik), Seçim (Geniş), Sağ Ok (Otomatik)
col1, col2, col3 = st.columns([1, 10, 1])

with col1:
    if st.button("<", key="prev_btn"):
        st.session_state.t_idx = (st.session_state.t_idx - 1) % len(takimlar)
        st.rerun()

with col2:
    if st.session_state.t_idx >= len(takimlar): st.session_state.t_idx = 0
    current_takim = st.selectbox("box", takimlar, index=st.session_state.t_idx, label_visibility="collapsed")
    st.session_state.t_idx = takimlar.index(current_takim)

with col3:
    if st.button(">", key="next_btn"):
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
        
        # Renk Belirleme
        color = "#ff0000" if iyms in ["1/2", "2/1"] else ("#f39c12" if iyms in ["1/0", "2/0"] else "#adb5bd")
        
        st.markdown(f"""
            <div class="match-row">
                <div style="font-size:11px; width:55px; color:gray;">{r['season']}</div>
                <div style="text-align:center; flex-grow:1;">
                    <div style="font-size:14px;">{r['home_team']} <span class="ms-val">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}</div>
                    <span class="iy-val">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</span>
                </div>
                <div class="badge" style="background-color:{color};">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info(f"🤖 {current_takim} için {hafta}. hafta verisi bulunamadı.")
