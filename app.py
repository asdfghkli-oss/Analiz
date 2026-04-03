import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları (Beyaz tema için varsayılan light mod)
st.set_page_config(page_title="Analiz Botu", layout="centered")

# Beyaz Tema ve Kırmızı Sürpriz Vurgusu (CSS)
st.markdown("""
    <style>
    /* Ana Arka Plan Beyaz */
    .stApp { background-color: #ffffff; }
    
    /* Seçim Kutuları */
    .stSelectbox div, .stNumberInput div { 
        background-color: #f0f2f6 !important; 
        color: #333 !important; 
        border-radius: 10px !important;
    }
    
    /* Tek Satır Maç Kartı (Açık Renk) */
    .match-row {
        background-color: #f8f9fa;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid #dee2e6;
        color: #212529;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .season-tag { color: #6c757d; font-size: 13px; font-weight: bold; width: 65px; }
    .teams-text { flex-grow: 1; text-align: center; font-size: 15px; font-weight: 500; }
    
    .score-badge { 
        background-color: #e9ecef; 
        padding: 2px 10px; 
        border-radius: 5px; 
        font-weight: bold; 
        color: #000;
        margin: 0 10px;
    }

    /* İY/MS Etiketleri */
    .iyms-normal { 
        background-color: #adb5bd; 
        color: white; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-size: 12px; 
        font-weight: bold;
        width: 55px;
        text-align: center;
    }

    /* SÜPRİZ (1/2 - 2/1) VURGUSU */
    .iyms-supriz { 
        background-color: #ff0000; 
        color: #ffffff; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-size: 13px; 
        font-weight: 900;
        width: 55px;
        text-align: center;
        box-shadow: 0 0 8px rgba(255,0,0,0.5);
        animation: pulse 2s infinite;
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
    ORDER BY season DESC
"""
df = query_db(sql)

if not df.empty:
    st.markdown(f"<p style='color:#6c757d; font-size:14px; font-weight:bold;'>{secilen_takim} - Geçmiş {hafta}. Hafta Maçları</p>", unsafe_allow_html=True)
    
    for _, r in df.iterrows():
        iyms = get_iyms(r['ht_home_score'], r['ht_away_score'], r['home_score'], r['away_score'])
        
        # Sürpriz kontrolü (1/2 veya 2/1 ise kırmızı yap)
        is_supriz = iyms in ["1/2", "2/1"]
        badge_class = "iyms-supriz" if is_supriz else "iyms-normal"
        
        # Tek Satır Tasarımı
        st.markdown(f"""
            <div class="match-row">
                <div class="season-tag">{r['season']}</div>
                <div class="teams-text">
                    {r['home_team']} <span class="score-badge">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}
                </div>
                <div class="{badge_class}">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("🤖 Bu takım için geçmişte bu haftaya ait maç kaydı bulunamadı.")
