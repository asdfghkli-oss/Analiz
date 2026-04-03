import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu Pro", layout="centered")

# Modern Buz Mavisi Tema & Renkli İY/MS Vurguları (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    .stSelectbox div, .stNumberInput div { 
        background-color: #ffffff !important; 
        border: 1px solid #d1d9e0 !important;
        border-radius: 12px !important;
    }
    
    .match-row {
        background-color: #eef2f7; 
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid #5c7f9a;
        color: #2c3e50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .season-tag { color: #5c7f9a; font-size: 12px; font-weight: bold; width: 60px; }
    
    .teams-container { 
        flex-grow: 1; 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
    }
    
    .ms-score { 
        font-size: 17px; 
        font-weight: 800; 
        color: #1a1a1a; 
        margin: 0 10px;
    }
    
    .iy-score-sub { 
        font-size: 11px; 
        color: #7f8c8d; 
        font-weight: bold;
        margin-top: -2px;
    }

    /* GENEL ETİKET STİLİ */
    .iyms-base { 
        padding: 5px 8px; 
        border-radius: 6px; 
        font-size: 12px; 
        font-weight: bold;
        width: 55px;
        text-align: center;
    }

    /* NORMAL SONUÇLAR (Gri) */
    .iyms-normal { background-color: #95a5a6; color: white; }

    /* SÜRPRİZ (1/2 - 2/1) - KIRMIZI */
    .iyms-supriz { 
        background-color: #e74c3c; 
        color: #ffffff; 
        font-size: 13px;
        font-weight: 900;
        box-shadow: 0 0 10px rgba(231,76,60,0.4);
        animation: pulse 1.5s infinite;
    }

    /* BERABERLİK (1/0 - 2/0) - KOYU SARI */
    .iyms-beraberlik { 
        background-color: #f39c12; /* Koyu Sarı / Turuncu */
        color: #ffffff; 
        font-size: 13px;
        font-weight: 900;
        box-shadow: 0 0 8px rgba(243,156,18,0.4);
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.08); }
        100% { transform: scale(1); }
    }
    
    h2, label { color: #2c3e50 !important; font-family: sans-serif; }
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

st.markdown("<h2 style='text-align:center;'>⚽ PRO ANALİZ BOTU</h2>", unsafe_allow_html=True)

# --- ÜST SEÇİM ALANI ---
c1, c2 = st.columns(2)
with c1:
    ligler = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("🏆 Lig Seç", ligler['league'].tolist() if not ligler.empty else [])
with c2:
    takimlar = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("⚽ Takım Seç", takimlar['home_team'].tolist() if not takimlar.empty else [])

hafta = st.number_input("🔢 Hafta (Round)", 1, 45, 30)

st.markdown("---")

# --- VERİ SORGUSU ---
sql = f"""
    SELECT season, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC
"""
df = query_db(sql)

if not df.empty:
    st.markdown(f"<p style='color:#5c7f9a; font-size:14px; font-weight:bold; text-align:center;'>{secilen_takim} - Geçmiş {hafta}. Hafta Analizi</p>", unsafe_allow_html=True)
    
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        # Renk Belirleme Mantığı
        if iyms in ["1/2", "2/1"]:
            badge_class = "iyms-supriz"
        elif iyms in ["1/0", "2/0"]:
            badge_class = "iyms-beraberlik"
        else:
            badge_class = "iyms-normal"
        
        # Tek Satır Tasarımı
        st.markdown(f"""
            <div class="match-row">
                <div class="season-tag">{r['season']}</div>
                <div class="teams-container">
                    <div style="font-size:14px;">{r['home_team']} <span class="ms-score">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}</div>
                    <div class="iy-score-sub">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</div>
                </div>
                <div class="iyms-base {badge_class}">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("🤖 Bu kriterlere uygun geçmiş maç kaydı bulunamadı.")
