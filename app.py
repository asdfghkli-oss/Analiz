import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Analiz Paneli", layout="wide")

# Veri Yükleme
@st.cache_data
def load_my_data():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        data.columns = [str(c).strip() for c in data.columns]
        return data
    return None

df = load_my_data()

st.title("⚽ Takım Karşılaştırmalı Analiz")

if df is not None and not df.empty:
    # 1. SEÇİMLER
    col_l, col_h = st.columns([3, 1])
    with col_l:
        lig_list = sorted(df['League'].unique().astype(str))
        secilen_lig = st.selectbox("🏆 Ligi Seçin", lig_list)
    with col_h:
        hafta_no = st.number_input("📅 Lig Haftası", 1, 45, 30)

    # Lig Filtresi
    lig_df = df[df['League'] == secilen_lig]
    takimlar = sorted(pd.concat([lig_df['HomeTeam'], lig_df['AwayTeam']]).unique().astype(str))

    st.markdown("---")
    
    # Takım Seçimleri
    c1, c2 = st.columns(2)
    with c1:
        ev_sahibi = st.selectbox("🏠 Ev Sahibi", takimlar)
    with c2:
        deplasman = st.selectbox("🚀 Deplasman", takimlar, index=1 if len(takimlar)>1 else 0)

    # 2. VERİ SÜZME (Burada hata payını sıfıra indirdik)
    # Ev sahibi için o haftadaki tüm maçlar
    ev_filtre = ((df['HomeTeam'] == ev_sahibi) | (df['AwayTeam'] == ev_sahibi))
    if 'Wk' in df.columns:
        ev_gecmis = df[ev_filtre & (df['Wk'].astype(str) == str(hafta_no))].sort_values(by='Date', ascending=False)
    else:
        ev_gecmis = df[ev_filtre].head(10)

    # Deplasman için o haftadaki tüm maçlar
    dep_filtre = ((df['HomeTeam'] == deplasman) | (df['AwayTeam'] == deplasman))
    if 'Wk' in df.columns:
        dep_gecmis = df[dep_filtre & (df['Wk'].astype(str) == str(hafta_no))].sort_values(by='Date', ascending=False)
    else:
        dep_gecmis = df[dep_filtre].head(10)

    # 3. GÖSTERİM
    st.subheader(f"🏟️ {hafta_no}. Hafta Geçmiş Skorları")
    
    t1, t2 = st.columns(2)
    
    # Sütunları hazırla
    gorunur_sutunlar = ['Date', 'HomeTeam', 'Score', 'AwayTeam']
    if 'HT' in df.columns: gorunur_sutunlar.insert(3, 'HT')

    with t1:
        st.info(f"🏠 {ev_sahibi} Geçmişi")
        if not ev_gecmis.empty:
            st.dataframe(ev_gecmis[gorunur_sutunlar], use_container_width=True)
        else:
            st.warning("Veri bulunamadı.")

    with t2:
        st.info(f"🚀 {deplasman} Geçmişi")
        if not dep_gecmis.empty:
            st.dataframe(dep_gecmis[gorunur_sutunlar], use_container_width=True)
        else:
            st.warning("Veri bulunamadı.")

else:
    st.error("🚨 Veri henüz yüklenmedi. Lütfen Actions bitene kadar bekleyin.")
