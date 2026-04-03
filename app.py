import streamlit as st
import sqlite3
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Analiz Botu Pro", layout="centered")

# --- TEMA SİSTEMİ ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

# --- TAKIM DEĞİŞTİRME MANTIĞI (OKLAR) ---
def query_db(sql):
    try:
        with sqlite3.connect("football.db") as conn:
            return pd.read_sql_query(sql, conn)
    except: return pd.DataFrame()

# Lig ve Takım Listelerini Al
ligler_df = query_db("SELECT DISTINCT league FROM matches ORDER BY league")
ligler = ligler_df['league'].tolist() if not ligler_df.empty else []

# CSS ile Görsel Düzenleme (Beyaz Bar Kaldırıldı)
st.markdown(f"""
    <style>
    .stApp {{ background-color: {'#ffffff' if st.session_state.theme == 'Light' else '#17212b'}; }}
    
    /* Üst Bar ve Gereksiz Boşlukları Kaldır */
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 1rem;}}
    
    /* Takım Değiştirme Alanı */
    .nav-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: {'#f8f9fa' if st.session_state.theme == 'Light' else '#242f3d'};
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
    }}
    
    /* Analiz Kutusu (Container) */
    .analysis-container {{
        background-color: {'#ffffff' if st.session_state.theme == 'Light' else '#1e2c3a'};
        border-radius: 12px;
        padding: 5px;
        border: 1px solid {'#eeeeee' if st.session_state.theme == 'Light' else '#2b3948'};
        margin-top: 5px;
    }}
    
    .match-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
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
        width: 50px;
        text-align: center;
    }}
    .bg-supriz {{ background-color: #ff0000; color: white; }}
    .bg-draw {{ background-color: #f39c12; color: white; }}
    .bg-normal {{ background-color: #dee2e6; color: #495057; }}
    </style>
    """, unsafe_allow_html=True)

# Sidebar Ayarları
with st.sidebar:
    st.session_state.theme = st.radio("Görünüm", ['Light', 'Dark'])
    secilen_lig = st.selectbox("🏆 Lig", ligler)

# Seçilen lige göre takımları getir
takimlar_df = query_db(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}' ORDER BY home_team")
takimlar = takimlar_df['home_team'].tolist() if not takimlar_df.empty else []

if 't_idx' not in st.session_state: st.session_state.t_idx = 0

# --- HAFTA EN ÜSTE ---
hafta = st.number_input("🔢 ANALİZ HAFTASI", 1, 45, 30)

# --- OKLARLA TAKIM SEÇİMİ ---
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if st.button(" < "):
        st.session_state.t_idx = (st.session_state.t_idx - 1) % len(takimlar)
with col2:
    current_takim = takimlar[st.session_state.t_idx]
    st.markdown(f"<h3 style='text-align:center; margin:0;'>{current_takim}</h3>", unsafe_allow_html=True)
with col3:
    if st.button(" > "):
        st.session_state.t_idx = (st.session_state.t_idx + 1) % len(takimlar)

# --- VERİ SORGUSU ---
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
                <div style="font-size:11px; width:50px;">{r['season']}</div>
                <div style="text-align:center; flex-grow:1;">
                    <div>{r['home_team']} <span class="ms-val">{int(r['home_score'])}-{int(r['away_score'])}</span> {r['away_team']}</div>
                    <span class="iy-val">İY: {int(r['ht_home_score'])}-{int(r['ht_away_score'])}</span>
                </div>
                <div class="badge {b_class}">{iyms}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.write(f"<p style='text-align:center; color:gray;'>{hafta}. haftaya ait veri bulunamadı.</p>", unsafe_allow_html=True)
