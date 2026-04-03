import streamlit as st
import pandas as pd
import os
from collections import Counter

# Sayfa Genişliği
st.set_page_config(page_title="Pro Score AI", layout="wide")

# Görseldeki gibi şık kutucuklar için CSS
st.markdown("""
    <style>
    .score-card {
        padding: 10px; border-radius: 8px; margin: 5px;
        text-align: center; font-weight: bold; color: #1a1a1a;
    }
    .green { background-color: #a7f3d0; border: 1px solid #059669; }
    .blue { background-color: #bfdbfe; border: 1px solid #2563eb; }
    .purple { background-color: #ddd6fe; border: 1px solid #7c3aed; }
    .yellow { background-color: #fef08a; border: 1px solid #ca8a04; }
    .brown { background-color: #fed7aa; border: 1px solid #ea580c; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_data():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        data.columns = [str(c).strip() for c in data.columns]
        return data
    return None

df = get_data()

# --- ÜST MENÜ (GÖRSELDEKİ GİBİ) ---
t1, t2, t3 = st.columns([1, 2, 1])
with t1:
    tarih = st.date_input("Tarih Seç", value=pd.to_datetime("2026-04-03"))
with t2:
    if df is not None:
        takim_list = sorted(pd.concat([df['HomeTeam'], df['AwayTeam']]).unique())
        secilen_takim = st.selectbox("Takım veya Lig ismi ile ara...", takim_list)
with t3:
    algo = st.selectbox("Algoritma", ["Ms Algoritma", "İy Algoritma", "Gol Algoritması"])

if df is not None:
    # Seçilen takımın verilerini süz
    analiz_df = df[(df['HomeTeam'] == secilen_takim) | (df['AwayTeam'] == secilen_takim)].copy()
    
    # Skorları ve Gol Sayılarını Hesapla
    ms_skorlar = analiz_df['Score'].dropna().tolist()
    ms_goller = []
    iy_skorlar = [] # Eğer HT (İlk Yarı) verisi varsa buraya dolar
    iy_goller = []

    for s in ms_skorlar:
        try:
            parts = s.replace('–', '-').split('-')
            g1, g2 = int(parts[0]), int(parts[1])
            ms_goller.append(f"{g1+g2} Gol")
        except: continue

    # İstatiksel Dağılım Fonksiyonu
    def render_stats(data_list, color_class, title, icon):
        st.markdown(f"#### {icon} {title}")
        if not data_list:
            st.write("Veri yok")
            return
        
        counts = Counter(data_list)
        total = len(data_list)
        sorted_counts = counts.most_common(6) # En çok çıkan 6 taneyi al
        
        cols = st.columns(2)
        for i, (val, count) in enumerate(sorted_counts):
            perc = int((count / total) * 100)
            with cols[i % 2]:
                st.markdown(f"""<div class="score-card {color_class}">{val} ({perc}%) {count} kere</div>""", unsafe_allow_html=True)

    st.markdown("---")
    
    # --- 4'LÜ KART YAPISI ---
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        render_stats(ms_skorlar, "green", "Maç Skoru Tahminleri", "🏟️")
    with row1_col2:
        # İy verisi varsa iy_skorlar buraya gelecek, şimdilik ms ile örnekliyoruz
        render_stats(ms_skorlar, "blue", "İlk Yarı Skoru Tahminleri", "⏱️")

    st.markdown("<br>", unsafe_allow_html=True)
    
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        render_stats(ms_goller, "purple", "Maç Sonu Gol Sayısı", "🌟")
    with row2_col2:
        # Örnek olarak ms_goller kullanıldı
        render_stats(ms_goller, "brown", "İlk Yarı Gol Sayısı", "⚽")

else:
    st.error("Veri dosyası bulunamadı!")
