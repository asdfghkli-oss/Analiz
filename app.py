import streamlit as st
import sqlite3
import pandas as pd

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Yapay Zeka Analiz", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

# Veritabanı Bağlantı Fonksiyonu
def get_connection():
    try:
        return sqlite3.connect('football.db', check_same_thread=False)
    except:
        st.error("Veritabanı (football.db) bulunamadı! Lütfen GitHub'a yüklediğinizden emin olun.")
        return None

# 1. BÜLTEN GETİRME
def bulten_cek(tarih):
    conn = get_connection()
    if conn:
        # Tarih formatını veritabanına göre ayarlar (YYYY-MM-DD)
        query = f"SELECT home_team, away_team, league, week FROM matches WHERE date = '{tarih}'"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# 2. HAFTALIK DÖNGÜ ANALİZİ
def analiz_motoru(takim, hafta, lig):
    conn = get_connection()
    if conn:
        # Takımın geçmiş 5 yıldaki aynı hafta maçları
        query = f"""
        SELECT * FROM matches 
        WHERE (home_team = '{takim}' OR away_team = '{takim}') 
        AND week = '{hafta}' AND league = '{lig}'
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# --- ARAYÜZ (FİLTRELER) ---
col1, col2, col3 = st.columns(3)

with col1:
    tarih_input = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    tarih_str = tarih_input.strftime('%Y-%m-%d')

# Bülten Yükleme
bulten = bulten_cek(tarih_str)

with col2:
    if not bulten.empty:
        bulten['mac'] = bulten['home_team'] + " - " + bulten['away_team']
        secilen_mac = st.selectbox("Günün Bülteni", bulten['mac'].tolist())
        m_info = bulten[bulten['mac'] == secilen_mac].iloc[0]
    else:
        st.warning("Bu tarihte maç bulunamadı.")
        secilen_mac = None

with col3:
    algoritma = st.selectbox("Algoritma Türü", 
                            ["İY/MS Sürpriz", "Skor Analizi", "Toplam Gol", "KG Var Analizi"])

st.divider()

# --- ANALİZ SONUÇLARI ---
if secilen_mac:
    res = analiz_motoru(m_info['home_team'], m_info['week'], m_info['league'])
    
    if not res.empty:
        st.subheader(f"🔍 {secilen_mac} ({m_info['week']}. Hafta Analizi)")
        
        # KUTUCUKLU GÖRÜNÜM MANTIĞI
        if algoritma == "İY/MS Sürpriz":
            st.info("🌟 Geçmişteki Sürpriz Sonuçlar (2/1, 1/2, 1/0, 2/0)")
            surpriz = res[res['iy_ms'].isin(['2/1', '1/2', '1/0', '2/0'])]
            if not surpriz.empty:
                st.dataframe(surpriz[['date', 'iy_skor', 'ms_skor', 'iy_ms']], use_container_width=True)
            else:
                st.write("Bu haftada geçmişte sürpriz sonuç bulunamadı.")

        elif algoritma == "Skor Analizi":
            skorlar = res['ms_skor'].value_counts()
            cols = st.columns(3)
            for i, (skor, count) in enumerate(skorlar.head(6).items()):
                yuzde = (count / len(res)) * 100
                cols[i % 3].success(f"**{skor}** \n %{yuzde:.1f} ({count} Kere)")

        elif algoritma == "Toplam Gol":
            # 2-3, 4-5, 6+ Gruplama
            res['gol_araligi'] = pd.cut(res['toplam_gol'].astype(int), bins=[-1, 1, 3, 5, 100], labels=['0-1', '2-3', '4-5', '6+'])
            gol_counts = res['gol_araligi'].value_counts()
            cols = st.columns(2)
            for i, (aralik, count) in enumerate(gol_counts.items()):
                cols[i % 2].warning(f"**{aralik} Gol** \n {count} Maç")

        elif algoritma == "KG Var Analizi":
            kg_var_maçlar = res[res['kg'] == 'Var']
            oran = (len(kg_var_maçlar) / len(res)) * 100
            st.metric("Karşılıklı Gol Var Olasılığı", f"%{oran:.1f}", f"Toplam {len(res)} Maçta")
            
    else:
        st.error("Bu maçın geçmişine dair veritabanında kayıtlı hafta döngüsü bulunamadı.")
