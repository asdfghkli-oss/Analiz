import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="LİG & VERİ ANALİZİ", layout="wide")

st.title("🔍 Tüm Dünya Veri Röntgeni (Son 30 Gün)")

if os.path.exists("all_leagues_data.csv"):
    df = pd.read_csv("all_leagues_data.csv")
    
    # 1. SÜTUNLAR (Algoritma için hayati önemde)
    st.subheader("📋 1. Sütun İsimleri (Kodda Bunları Kullanacağız)")
    st.code(list(df.columns))

    # 2. LİG İSİMLERİ (Filtreleme için hayati önemde)
    st.subheader("🌍 2. Sistemdeki Tüm Ligler (Alfabetik)")
    # 'Comp' sütunu genelde lig adıdır (Competition)
    comp_col = 'Comp' if 'Comp' in df.columns else (df.columns[5] if len(df.columns) > 5 else df.columns[0])
    
    ligler = sorted(df[comp_col].unique().astype(str))
    st.write(f"Toplam {len(ligler)} farklı lig bulundu.")
    st.multiselect("Lig Listesini Buradan İncele:", ligler, default=ligler[:5])

    # 3. HAM VERİ GÖRÜNÜMÜ
    st.subheader("🏟️ 3. Maç Listesi ve Skor Formatı")
    st.dataframe(df, use_container_width=True)

else:
    st.error("🚨 Veri dosyası boş! Lütfen GitHub Actions'ı çalıştırın.")
