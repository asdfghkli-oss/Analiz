import streamlit as st
import pandas as pd
import os
from collections import Counter

st.set_page_config(page_title="AI Skor Analiz", layout="wide")

# Görseldeki Kart Tasarımı İçin CSS
st.markdown("""
    <style>
    .score-box {
        padding: 12px; border-radius: 10px; margin: 6px;
        text-align: center; font-weight: 600; font-family: sans-serif;
    }
    .green { background-color: #BBF7D0; border: 1px solid #16A34A; color: #14532D; }
    .blue { background-color: #DBEafe; border: 1px solid #2563EB; color: #1E3A8A; }
    .purple { background-color: #E9D5FF; border: 1px solid #7C3AED; color: #4C1D95; }
    .yellow { background-color: #FEF08A; border: 1px solid #CA8A04; color: #713F12; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def veri_yukle():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        data.columns = [str(c).strip() for c in data.columns]
        return data
    return None

df = veri_yukle()

# --- ÜST PANEL ---
t1, t2, t3 = st.columns([1, 2, 1])
with t1:
    st.date_input("Tarih Seç", value=pd.to_datetime("2026-04-03"))
with t2:
    if df is not None:
        # Sütun isimlerini güvenli bul (HomeTeam veya Home)
        h_col = 'HomeTeam' if 'HomeTeam' in df.columns else 'Home'
        a_col = 'AwayTeam' if 'AwayTeam' in df.columns else 'Away'
        takimlar = sorted(pd.concat([df[h_col], df[a_col]]).unique())
        secilen_takim = st.selectbox("Takım veya Lig ismi ile ara...", takimlar)
with t3:
    st.selectbox("Algoritma", ["Ms Algoritma", "İy Algoritma"])

if df is not None:
    # SÜTUN KONTROLÜ (KeyError Çözümü)
    s_col = 'Score' if 'Score' in df.columns else (df.columns[4] if len(df.columns) > 4 else df.columns[0])
    
    # Veriyi Filtrele
    analiz_df = df[(df[h_col] == secilen_takim) | (df[a_col] == secilen_takim)].copy()
    
    # Hesaplamalar
    ms_skorlar = analiz_df[s_col].dropna().tolist()
    ms_gol_sayilari = []
    
    for s in ms_skorlar:
        try:
            pts = s.replace('–', '-').split('-')
            ms_gol_sayilari.append(f"{int(pts[0]) + int(pts[1])} Gol")
        except: continue

    # Kart Çizim Fonksiyonu
    def kartlari_bas(liste, renk, baslik, ikon):
        st.markdown(f"#### {ikon} {baslik}")
        if not liste:
            st.write("Veri bulunamadı.")
            return
        
        counts = Counter(liste)
        total = len(liste)
        en_cok = counts.most_common(6)
        
        c_left, c_right = st.columns(2)
        for i, (val, count) in enumerate(en_cok):
            yüzde = int((count/total)*100)
            kart_html = f'<div class="score-box {renk}">{val} ({yüzde}%) {count} kere</div>'
            if i % 2 == 0: c_left.markdown(kart_html, unsafe_allow_html=True)
            else: c_right.markdown(kart_html, unsafe_allow_html=True)

    st.markdown("---")
    
    # GÖRSELDEKİ 4'LÜ YAPI
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        kartlari_bas(ms_skorlar, "green", "Maç Skoru Tahminleri", "🏟️")
    with r1_c2:
        # İY verisi şimdilik simüle edildi, HT sütunu varsa oraya bağlanabilir
        kartlari_bas(ms_skorlar[:5], "blue", "İlk Yarı Skoru Tahminleri", "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)
    
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        kartlari_bas(ms_gol_sayilari, "purple", "Maç Sonu Gol Sayısı", "🌟")
    with r2_c2:
        kartlari_bas(ms_gol_sayilari[:4], "yellow", "İlk Yarı Gol Sayısı", "⚽")

else:
    st.error("all_leagues_data.csv bulunamadı!")
