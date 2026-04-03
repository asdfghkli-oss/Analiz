import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="PRO DÖNGÜ ANALİZ", layout="wide")

# Şık Karanlık Tema Tasarımı
st.markdown("""
    <style>
    .stMetric { background-color: #111827; border: 1px solid #374151; padding: 15px; border-radius: 10px; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        # Görseldeki sütun isimlerine göre temizlik
        data.columns = [str(c).strip() for c in data.columns]
        return data
    return None

df = load_data()

st.title("🤖 AI Periyot & Algoritma Analizörü")

if df is not None and not df.empty:
    # --- 1. ÜST SEÇİM PANELİ ---
    c1, c2, c3 = st.columns(3)
    with c1:
        ligler = sorted(df['League'].unique().astype(str))
        secilen_lig = st.selectbox("🏆 Lig Seçin", ligler)
    with c2:
        # Seçilen ligdeki takımları getir
        lig_df = df[df['League'] == secilen_lig]
        takimlar = sorted(pd.concat([lig_df['HomeTeam'], lig_df['AwayTeam']]).unique().astype(str))
        ev_sahibi = st.selectbox("🏠 Ev Sahibi Takım", takimlar)
    with c3:
        deplasman = st.selectbox("🚀 Deplasman Takım", takimlar, index=1 if len(takimlar)>1 else 0)

    # Döngü Haftası Seçimi
    hafta_no = st.slider("📅 Analiz Periyodu (Hafta Döngüsü)", 1, 42, 30)
    
    st.markdown("---")

    # --- 2. ALGORİTMA HESAPLAMA MOTORU ---
    def analiz_motoru(takim, hafta):
        # Takımın tüm geçmişindeki o haftayı bul (Wk sütunu varsa kullan, yoksa Date'ten çek)
        if 'Wk' in df.columns:
            return df[((df['HomeTeam'] == takim) | (df['AwayTeam'] == takim)) & (df['Wk'].astype(str) == str(hafta))]
        return df[((df['HomeTeam'] == takim) | (df['AwayTeam'] == takim))].head(10) # Yedek plan

    ev_gecmis = analiz_motoru(ev_sahibi, hafta_no)
    dep_gecmis = analiz_motoru(deplasman, hafta_no)

    # Skor Parçalama ve Oran Hesaplama
    def oran_hesapla(data):
        if data.empty: return 0, 0, 0
        kg, ust, iy_sıfır = 0, 0, 0
        for s in data['Score'].dropna():
            try:
                # 2–1 formatını temizle
                p = s.replace('–', '-').split('-')
                s1, s2 = int(p[0]), int(p[1])
                if s1 > 0 and s2 > 0: kg += 1
                if (s1 + s2) > 2.5: ust += 1
                # İY tahmini simülasyonu (Veride HT varsa ona bakılır)
                if s1 == s2: iy_sıfır += 1 
            except: continue
        toplam = len(data)
        return int((kg/toplam)*100), int((ust/toplam)*100), int((iy_sıfır/toplam)*100)

    kg_e, ust_e, iy_e = oran_hesapla(ev_gecmis)
    kg_d, ust_d, iy_d = oran_hesapla(dep_gecmis)

    # --- 3. GÖRSEL ANALİZ SONUÇLARI ---
    st.subheader(f"🧠 {ev_sahibi} vs {deplasman} - Algoritma Kararları")
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric("KG VAR Olasılığı", f"%{int((kg_e + kg_d)/2)}")
        st.write("**Karar:** " + ("KG VAR" if (kg_e+kg_d)/2 > 60 else "KG YOK"))
    with res2:
        st.metric("2.5 ÜST Olasılığı", f"%{int((ust_e + ust_d)/2)}")
        st.write("**Karar:** " + ("ÜST" if (ust_e+ust_d)/2 > 55 else "ALT"))
    with res3:
        st.metric("İY 0 Olasılığı", f"%{int((iy_e + iy_d)/2)}")
        st.write("**Karar:** İY 0 Denenebilir" if (iy_e+iy_d)/2 > 50 else "MS Odaklı")

    # --- 4. AYRI AYRI GEÇMİŞ LİSTELERİ ---
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader(f"🏠 {ev_sahibi} ({hafta_no}. Hafta Geçmişi)")
        st.table(ev_gecmis[['Date', 'HomeTeam', 'Score', 'AwayTeam']].head(5))
        
    with col_b:
        st.subheader(f"🚀 {deplasman} ({hafta_no}. Hafta Geçmişi)")
        st.table(dep_gecmis[['Date', 'HomeTeam', 'Score', 'AwayTeam']].head(5))

else:
    st.error("🚨 Veri dosyası henüz dolmadı. Lütfen Actions bitene kadar bekleyin.")
