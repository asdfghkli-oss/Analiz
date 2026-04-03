import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Karşılaştırmalı Analiz", layout="wide")

# Görsel Stil Ayarları
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stTable"] { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def veri_yukle():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        # Sütun isimlerindeki olası boşlukları temizle
        data.columns = [str(c).strip() for c in data.columns]
        return data
    return None

df = veri_yukle()

st.title("⚽ Takım Karşılaştırmalı Döngü Analizi")

if df is not None and not df.empty:
    # --- ÜST SEÇİM PANELİ ---
    col_lig, col_hafta = st.columns([3, 1])
    
    with col_lig:
        lig_listesi = sorted(df['League'].unique().astype(str))
        secilen_lig = st.selectbox("🏆 Analiz Edilecek Ligi Seçin", lig_listesi)
    
    with col_hafta:
        # FBref'te hafta 'Wk' olarak geçer, eğer yoksa sayı girişi yaptırır
        hafta_no = st.number_input("📅 Lig Haftası (Döngü)", 1, 45, 30)

    # Seçilen ligdeki takımları filtrele
    lig_df = df[df['League'] == secilen_lig]
    tum_takimlar = sorted(pd.concat([lig_df['HomeTeam'], lig_df['AwayTeam']]).unique().astype(str))

    st.markdown("---")
    
    # --- TAKIM SEÇİMLERİ ---
    c1, c2 = st.columns(2)
    with c1:
        ev_sahibi = st.selectbox("🏠 Ev Sahibi Takım", tum_takimlar)
    with c2:
        deplasman = st.selectbox("🚀 Deplasman Takım", tum_takimlar, index=1 if len(tum_takimlar)>1 else 0)

    # --- VERİ FİLTRELEME MOTORU ---
    # Takımların geçmişteki o haftaya (Wk) ait tüm maçlarını bul
    def periyot_getir(takim, hafta):
        # Wk sütunu yoksa Date'e göre son maçları getirir, varsa haftaya göre filtreler
        mask = (df['HomeTeam'] == takim) | (df['AwayTeam'] == takim)
        temp = df[mask]
        if 'Wk' in df.columns:
            return temp[temp['Wk'].astype(str) == str(hafta)].sort_values(by='Date', ascending=False)
        return temp.sort_values(by='Date', ascending=False).head(10)

    ev_gecmis = periyot_getir(ev_sahibi, hafta_no)
    dep_gecmis = periyot_getir(deplasman, hafta_no)

    # --- TABLOLARI YAN YANA GÖSTER ---
    st.subheader(f"🏟️ {hafta_no}. Hafta Geçmiş Performansları")
    
    tab_ev, tab_dep = st.columns(2)
    
    # İhtiyacımız olan sütunları belirleyelim
    cols = ['Date', 'HomeTeam', 'Score', 'AwayTeam']
    # Eğer İY (HT) skoru varsa listeye ekle
    if 'HT' in df.columns: cols.insert(3, 'HT') 

    with tab_ev:
        st.info(f"🏠 {ev_sahibi} - {hafta_no}. Hafta Maçları")
        if not ev_gecmis.empty:
            st.table(ev_gecmis[cols])
        else:
            st.warning("Bu hafta için geçmiş veri bulunamadı.")

    with tab_dep:
        st.info(f"🚀 {deplasman} - {hafta_no}. Hafta Maçları")
        if not dep_gecmis.empty:
            st.table(dep_gecmis[cols])
        else:
            st.warning("Bu hafta için geçmiş veri bulunamadı.")

else:
    st.error("🚨 Veri dosyası okunamadı. Lütfen 'Update' işleminin bittiğinden emin olun.")
