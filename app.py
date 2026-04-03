import streamlit as st
import sqlite3
import pandas as pd
from collections import Counter

st.set_page_config(page_title="AI PRO ANALİZ", layout="wide")

# Görseldeki Kart Tasarımı (CSS)
st.markdown("""
    <style>
    .card { padding: 12px; border-radius: 10px; margin: 5px; text-align: center; font-weight: bold; }
    .skor-ms { background-color: #BBF7D0; border: 1px solid #16A34A; color: #14532D; } /* Yeşil */
    .skor-iy { background-color: #DBEafe; border: 1px solid #2563EB; color: #1E3A8A; } /* Mavi */
    .gol-ms { background-color: #E9D5FF; border: 1px solid #7C3AED; color: #4C1D95; }  /* Mor */
    .gol-iy { background-color: #FEF08A; border: 1px solid #CA8A04; color: #713F12; }  /* Sarı */
    </style>
    """, unsafe_allow_html=True)

def veri_cek(sorgu):
    conn = sqlite3.connect("football.db")
    df = pd.read_sql_query(sorgu, conn)
    conn.close()
    return df

st.title("🤖 AI Periyot & Skor Analiz Sistemi")

# --- ÜST PANEL ---
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    tarih = st.date_input("Tarih Seç", value=pd.to_datetime("2026-04-03"))
with c2:
    # DB'den lig ve takım listesini çek
    ligler_df = veri_cek("SELECT DISTINCT league FROM matches ORDER BY league")
    secilen_lig = st.selectbox("Lig Seçin", ligler_df['league'])
    
    takimlar_df = veri_cek(f"SELECT DISTINCT home_team FROM matches WHERE league='{secilen_lig}'")
    secilen_takim = st.selectbox("Takım Seçin", takimlar_df['home_team'])
with c3:
    algo = st.selectbox("Algoritma", ["Ms Algoritma", "İy Algoritma", "Gol Analizi"])

# --- ANALİZ MOTORU ---
# Takımın son 5 yıldaki o haftadaki (periyot) verilerini çek
# Not: Tablonda 'week' veya 'round' sütunu olduğunu varsayıyoruz
analiz_df = veri_cek(f"""
    SELECT home_score, away_score, ht_home_score, ht_away_score 
    FROM matches 
    WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}')
""")

if not analiz_df.empty:
    # Skorları Formatla
    ms_skorlar = [f"{r['home_score']}-{r['away_score']}" for _, r in analiz_df.iterrows()]
    iy_skorlar = [f"{r['ht_home_score']}-{r['ht_away_score']}" for _, r in analiz_df.iterrows()]
    ms_toplam_gol = [f"{int(r['home_score'] + r['away_score'])} Gol" for _, r in analiz_df.iterrows()]
    iy_toplam_gol = [f"{int(r['ht_home_score'] + r['ht_away_score'])} Gol" for _, r in analiz_df.iterrows()]

    def kart_olustur(liste, stil, baslik, ikon):
        st.markdown(f"#### {ikon} {baslik}")
        counts = Counter(liste)
        total = len(liste)
        top_items = counts.most_common(6)
        
        col_l, col_r = st.columns(2)
        for i, (val, count) in enumerate(top_items):
            yuzde = int((count/total)*100)
            html = f'<div class="card {stil}">{val} ({yuzde}%) {count} kere</div>'
            if i % 2 == 0: col_l.markdown(html, unsafe_allow_html=True)
            else: col_r.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    
    # 4'LÜ KART YAPISI
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        kart_olustur(ms_skorlar, "skor-ms", "Maç Skoru Tahminleri", "🏟️")
    with row1_c2:
        kart_olustur(iy_skorlar, "skor-iy", "İlk Yarı Skoru Tahminleri", "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)
    
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        kart_olustur(ms_toplam_gol, "gol-ms", "Maç Sonu Gol Sayısı", "🌟")
    with row2_c2:
        kart_olustur(iy_toplam_gol, "gol-iy", "İlk Yarı Gol Sayısı", "⚽")
else:
    st.warning("Seçilen takıma ait geçmiş veri bulunamadı.")
