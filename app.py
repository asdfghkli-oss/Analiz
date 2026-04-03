import streamlit as st
import sqlite3
import pandas as pd

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Pro Analiz Paneli", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# 1. GÜNÜN BÜLTENİNİ ÇEKME
def get_bulten(tarih):
    conn = get_conn()
    # Senin veritabanındaki current_bulletin tablosundan çekiyoruz
    query = f"SELECT home_team, away_team, league, round FROM current_bulletin WHERE date = '{tarih}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 2. HAFTALIK DÖNGÜ ANALİZİ (GEÇMİŞ VERİ)
def get_analiz(takim, round_no, lig):
    conn = get_conn()
    # matches tablosundaki sütun isimlerine (round, league) göre sorgu
    query = f"""
    SELECT * FROM matches 
    WHERE (home_team = '{takim}' OR away_team = '{takim}') 
    AND round = '{round_no}' AND league = '{lig}'
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- ARAYÜZ ---
col1, col2, col3 = st.columns(3)

with col1:
    secilen_tarih = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    tarih_str = secilen_tarih.strftime('%Y-%m-%d')

# Bülteni Yükle
bulten_df = get_bulten(tarih_str)

with col2:
    if not bulten_df.empty:
        bulten_df['mac_adi'] = bulten_df['home_team'] + " - " + bulten_df['away_team']
        secilen_mac = st.selectbox("Günün Bülteni", bulten_df['mac_adi'].tolist())
        m = bulten_df[bulten_df['mac_adi'] == secilen_mac].iloc[0]
    else:
        st.warning("Bu tarihte bülten bulunamadı.")
        secilen_mac = None

with col3:
    algoritma = st.selectbox("Algoritma Seçin", 
                            ["İY/MS & Oran Analizi", "Skor Analizi", "Toplam Gol (Alt/Üst)", "KG Var Analizi"])

st.divider()

# --- ANALİZ SONUÇLARI ---
if secilen_mac:
    # 'round' sütununu kullanarak geçmişteki aynı hafta döngüsünü buluyoruz
    res = get_analiz(m['home_team'], m['round'], m['league'])
    
    if not res.empty:
        st.subheader(f"🔍 {secilen_mac} ({m['round']}. Hafta Analizi)")
        
        if algoritma == "İY/MS & Oran Analizi":
            st.info("🎯 Geçmişteki Skor ve İddaa Oranları")
            # ht_home_score ve ht_away_score sütunlarını kullanarak İY oluşturuyoruz
            res['iy_skor'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
            res['ms_skor'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
            st.dataframe(res[['date', 'iy_skor', 'ms_skor', 'iddaa_ms1', 'iddaa_msx', 'iddaa_ms2']], use_container_width=True)
            
        elif algoritma == "Skor Analizi":
            res['skor'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
            skorlar = res['skor'].value_counts().head(6)
            sc1, sc2, sc3 = st.columns(3)
            for i, (skor, count) in enumerate(skorlar.items()):
                yuzde = (count / len(res)) * 100
                col = [sc1, sc2, sc3][i % 3]
                col.success(f"**{skor}** \n %{yuzde:.1f} ({count} Kere)")

        elif algoritma == "Toplam Gol (Alt/Üst)":
            st.warning("🥅 Alt/Üst 2.5 Dağılımı")
            alt_ust = res['alt_ust_25'].value_counts()
            gc1, gc2 = st.columns(2)
            for i, (durum, count) in enumerate(alt_ust.items()):
                col = [gc1, gc2][i % 2]
                col.metric(f"2.5 {durum}", f"{count} Maç")

        elif algoritma == "KG Var Analizi":
            kg_v = res[res['kg_result'] == 'Var'].shape[0]
            oran = (kg_v / len(res)) * 100
            st.metric("Karşılıklı Gol Var Olasılığı", f"%{oran:.1f}", f"{kg_v}/{len(res)} Maç")
    else:
        st.error("Bu maçın geçmişine dair aynı hafta/lig verisi bulunamadı.")
