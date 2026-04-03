import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Mega Döngü Analiz", layout="wide")
st.title("🔄 5 Yıllık Hafta & Periyot Analizörü")

# Veriyi oku ve sütunları temizle
@st.cache_data
def load_data():
    if os.path.exists("all_leagues_data.csv"):
        data = pd.read_csv("all_leagues_data.csv")
        # Sütun isimlerindeki boşlukları temizle
        data.columns = [str(c).strip() for c in data.columns]
        return data
    return None

df = load_data()

if df is not None and not df.empty:
    # SÜTUN KONTROLÜ (Hata almamak için dinamik isim bulma)
    # FBref'ten gelen olası sütun isimleri
    lig_col = next((c for c in df.columns if 'League' in c or 'Comp' in c), df.columns[0])
    home_col = next((c for c in df.columns if 'Home' in c), df.columns[2])
    wk_col = next((c for c in df.columns if 'Wk' in c or 'Round' in c), df.columns[1])
    
    st.sidebar.success(f"✅ {len(df)} maç yüklendi.")

    # Filtreler
    with st.sidebar:
        st.header("🔍 Analiz Filtresi")
        ligler = sorted(df[lig_col].unique().astype(str))
        secilen_lig = st.selectbox("Lig Seç:", ligler)
        
        # Seçilen lige göre takımları filtrele
        lig_df = df[df[lig_col] == secilen_lig]
        takimlar = sorted(lig_df[home_col].unique().astype(str))
        secilen_takim = st.selectbox("Takım Seç:", takimlar)
        
        hafta = st.slider("Hangi Haftayı Analiz Edelim?", 1, 42, 30)

    # ANALİZ MOTORU
    # Takımın hem ev hem deplasman maçlarını bul
    away_col = next((c for c in df.columns if 'Away' in c), df.columns[3])
    
    analiz_df = df[
        ((df[home_col] == secilen_takim) | (df[away_col] == secilen_takim)) & 
        (df[wk_col].astype(str) == str(hafta))
    ].sort_values(by=df.columns[0], ascending=False) # İlk sütuna (tarih/sezon) göre sırala

    st.subheader(f"📊 {secilen_takim} - {hafta}. Hafta Döngüsü")
    
    if not analiz_df.empty:
        # İhtiyacımız olan sütunları güvenli şekilde göster
        gosterilecek = [c for c in ['Season', lig_col, home_col, 'Score', away_col] if c in analiz_df.columns]
        st.dataframe(analiz_df[gosterilecek], use_container_width=True)
    else:
        st.warning(f"⚠️ {secilen_takim} için {hafta}. haftada geçmiş veri bulunamadı.")
else:
    st.error("🚨 Veri dosyası boş veya hatalı çekilmiş. Lütfen Actions sekmesinden tekrar 'Run Workflow' yapın ve bitmesini bekleyin.")
