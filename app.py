import streamlit as st

st.set_page_config(page_title="Analiz Paneli", layout="wide")

st.title("🏟️ Yapay Zeka Destekli Analiz")

# Üst Menü
col1, col2, col3 = st.columns(3)
with col1:
    st.date_input("Tarih Seç")
with col2:
    st.text_input("Takım veya Lig ara...", "Mallorca")
with col3:
    st.selectbox("Algoritma", ["Ms Algoritma", "İY Analizi"])

# Analiz Kutucukları
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.info("🏟️ Maç Skoru Tahminleri")
    sc1, sc2 = st.columns(2)
    sc1.success("3-2 (%33) 3 kere")
    sc2.success("2-0 (%22) 2 kere")
    sc1.success("3-0 (%11) 1 kere")
    sc2.success("2-2 (%11) 1 kere")

with c2:
    st.info("⏱️ İlk Yarı Skoru Tahminleri")
    ic1, ic2 = st.columns(2)
    ic1.button("2-1 (%44) 4 kere", use_container_width=True)
    ic2.button("1-0 (%22) 2 kere", use_container_width=True)
    ic1.button("0-0 (%11) 1 kere", use_container_width=True)
    ic2.button("2-0 (%11) 1 kere", use_container_width=True)
