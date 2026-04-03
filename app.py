import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu", layout="centered")

# Beyaz Tema & Net Renk Vurguları (CSS)
st.markdown("""
    <style>
    /* Arka Planı Tekrar Beyaz Yapıyoruz */
    .stApp { background-color: #ffffff; }
    
    /* Seçim Kutuları */
    .stSelectbox div, .stNumberInput div { 
        background-color: #f8f9fa !important; 
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
    }
    
    /* Maç Satırı (Beyaz/Çok Açık Gri) */
    .match-row {
        background-color: #ffffff; 
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #f1f1f1;
        border-left: 5px solid #333; /* Sol kenar çubuğu sade siyah/gri */
        color: #212529;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .season-tag { color: #6c757d; font-size: 13px; font-weight: bold; width: 65px; }
    
    .teams-container { 
        flex-grow: 1; 
        text-align: center; 
        display: flex; 
        flex-direction: column; 
    }
    
    .ms-score { 
        font-size: 18px; 
        font-weight: bold; 
        color: #000; 
        margin: 0 10px;
    }
    
    .iy-score-sub { 
        font-size: 11px; 
        color: #888; 
        font-weight: bold;
        margin-top: -2px;
    }

    /* İY/MS BUTONLARI */
    .iyms-base { 
        padding: 5px 8px; 
        border-radius: 6px; 
        font-size: 12px; 
        font-weight: bold;
        width: 55px;
        text-align: center;
    }

    /* NORMAL (Gri) */
    .iyms-normal { background-color: #e9ecef; color: #495057; }

    /* SÜRPRİZ (1/2 - 2/1) - KIRMIZI */
    .iyms-supriz { 
        background-color: #ff0000; 
        color: white; 
        box-shadow: 0 0 8px rgba(255,0,0,0.3);
        animation: pulse 1.5s infinite;
    }

    /* BERABERLİK (1/0 - 2/0) - KOYU SARI */
    .iyms-beraberlik { 
        background-color: #ffc107; /* Canlı Sarı */
        color: #000; 
        border: 1px solid #e0a800;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    h2, label { color: #333 !important; }
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

# --- ANALİZ LİSTESİ ---
sql = f"""
    SELECT season, home_team, away_team, home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
    AND round = {hafta}
    ORDER BY season DESC
"""
df = query_db(sql)

if not df.empty:
    st.markdown(f"<p style='color:#666; font-size:14px; text-align:center;'>{secilen_takim} - Geçmiş {hafta}. Hafta</p>", unsafe_allow_html=True)
    
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        # Renk Kontrolü
        if iyms in ["1/2", "2/1"]:
            badge_class = "iyms-supriz"
        elif iyms in ["1/0", "2/0"]:
            badge_class = "iyms-beraberlik"
        else:
            badge_class = "iyms-normal"
        
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
