import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu Pro", layout="centered")

# --- TEMA SİSTEMİ ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    st.session_state.theme = st.radio("Görünüm Modu", ['Light', 'Dark'])

# --- DİNAMİK STİL (BELİRGİN TABLO ETKİSİ) ---
if st.session_state.theme == 'Dark':
    bg_color = "#17212b"
    text_color = "#ffffff"
    table_bg = "#1e2c3a"  # Arka plandan biraz daha açık/belirgin dark
    row_border = "#2b3948"
    sub_text = "#95a5a6"
    accent = "#5288c1"
else:
    bg_color = "#f4f7f9"  # Genel arka plan hafif gri
    text_color = "#212529"
    table_bg = "#ffffff"  # Tablo alanı bembeyaz parlayacak
    row_border = "#e9ecef"
    sub_text = "#6c757d"
    accent = "#333333"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    
    /* ANALİZ TABLO ALANI (Kapsayıcı) */
    .analysis-container {{
        background-color: {table_bg};
        border-radius: 12px;
        padding: 10px;
        border: 1px solid {row_border};
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); /* "Ben buradayım" diyen hafif gölge */
        margin-top: 20px;
    }}
    
    /* Maç Satırı (Düz ve Net) */
    .match-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 10px;
        border-bottom: 1px solid {row_border};
        color: {text_color};
    }}
    .match-row:last-child {{ border-bottom: none; }}
    
    .season-tag {{ color: {sub_text}; font-size: 12px; font-weight: bold; width: 60px; }}
    
    .score-box {{ text-align: center; flex-grow: 1; }}
    .ms-val {{ font-size: 18px; font-weight: 800; margin: 0 5px; }}
    .iy-val {{ font-size: 11px; color: {sub_text}; font-weight: bold; display: block; margin-top: -2px; }}

    /* İY/MS ETİKETLERİ */
    .badge {{
        padding: 5px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 900;
        width: 55px;
        text-align: center;
    }}
    .bg-normal {{ background-color: #dee2e6; color: #495057; }}
    .bg-supriz {{ background-color: #ff0000; color: white; box-shadow: 0 0 10px rgba(255,0,0,0.4); }}
    .bg-draw {{ background-color: #f39c12; color: white; }}

    h2, label, p {{ color: {text_color} !important; font-family: 'Segoe UI', sans-serif; }}
    hr {{ border-top: 1px solid {row_border}; }}
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

st.markdown("<h2 style='text-align:center;'>📊 İSTATİSTİK BOTU</h2>", unsafe_allow_html=True)

# --- FİLTRELER ---
c1, c2 = st.columns(2)
with c1:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig", ligler['league'].tolist() if not ligler.empty else [])
with c2:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım", takimlar['home_team'].tolist() if not takimlar.empty else [])

hafta = st.number_input("🔢 Hafta (Round)", 1, 45, 30)

# --- VERİ ANALİZ ALANI ---
sql = f"""
    SELECT season, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC LIMIT 5
"""
df = query_db(sql)

if not df.empty:
    st.markdown("---")
    # Tüm maçları kapsayan belirgin ana kutu (Container)
    st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
    
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        # Renk Belirleme
        if iyms in ["1/2", "2/1"]: b_class = "bg-supriz"
        elif iyms in ["1/0", "2/0"]: b_class = "bg-draw"
        else: b_class = "bg-normal"
        
        st.markdown(f"""
            <div class="match-row">
                <div class="season-tag">{r['season']}</div>
                <div class="score-box">
                    <div>{r['home_team']} <span class="ms-val">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}</div>
                    <span class="iy-val">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</span>
                </div>
                <div class="badge {b_class}">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("🤖 Bu kriterlere uygun maç kaydı bulunamadı.")
