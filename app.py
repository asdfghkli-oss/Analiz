import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz Sistemi", layout="wide")
st.title("⚽ Profesyonel Maç Analiz Arşivi")

if not os.path.exists("all_leagues_data.csv"):
    st.error("Veri bulunamadı. Lütfen Actions üzerinden güncelleyin.")
else:
    df = pd.read_csv("all_leagues_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    # --- FİLTRELER ---
    with st.sidebar:
        st.header("🔍 Filtreleme")
        ligler = sorted(df['League'].unique())
        secilen_lig = st.selectbox("Lig Seç", ligler)
        
        lig_df = df[df['League'] == secilen_lig].copy()
        
        takimlar = sorted(pd.concat([lig_df['HomeTeam'], lig_df['AwayTeam']]).unique())
        secilen_takim = st.selectbox("Takım Analizi (Opsiyonel)", ["Hepsi"] + takimlar)
        
        hafta_araligi = st.slider("Hafta Aralığı", 1, int(lig_df['Week'].max()), (1, int(lig_df['Week'].max())))

    # --- VERİ İŞLEME ---
    display_df = lig_df[(lig_df['Week'] >= hafta_araligi[0]) & (lig_df['Week'] <= hafta_araligi[1])]
    
    if secilen_takim != "Hepsi":
        display_df = display_df[(display_df['HomeTeam'] == secilen_takim) | (display_df['AwayTeam'] == secilen_takim)]

    # Skor Formatlama
    display_df['İY'] = display_df['HTHG'].astype(str).str.replace('.0','',regex=False) + "-" + display_df['HTAG'].astype(str).str.replace('.0','',regex=False)
    display_df['MS'] = display_df['FTHG'].astype(str).str.replace('.0','',regex=False) + "-" + display_df['FTAG'].astype(str).str.replace('.0','',regex=False)
    
    # --- GÖRÜNÜM ---
    st.subheader(f"📊 {secilen_lig} - {secilen_takim} Analiz Tablosu")
    
    final_table = display_df[['Week', 'Date', 'HomeTeam', 'AwayTeam', 'İY', 'MS']].sort_values(by='Week', ascending=False)
    
    st.dataframe(final_table, use_container_width=True)

    # --- İSTATİSTİK ÖZETİ ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        ms_skorlar = final_table['MS'].value_counts().head(3)
        st.write("🔝 **En Sık MS Skorları**")
        st.write(ms_skorlar)
        
    with c2:
        iy_skorlar = final_table['İY'].value_counts().head(3)
        st.write("🔝 **En Sık İY Skorları**")
        st.write(iy_skorlar)
        
    with c3:
        toplam_mac = len(final_table)
        ust_mac = len(display_df[(display_df['FTHG'] + display_df['FTAG']) > 2.5])
        st.metric("2.5 Üst Oranı", f"%{round((ust_mac/toplam_mac)*100, 1)}" if toplam_mac > 0 else "0")
