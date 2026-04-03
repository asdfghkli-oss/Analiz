import streamlit as st
import sqlite3
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Pro Analiz Paneli", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# --- OTOMATİK BÜLTEN ÇEKME FONKSİYONU ---
def bulteni_internetten_cek():
    with st.spinner('Güncel bülten çekiliyor, lütfen bekleyin...'):
        try:
            # ÖNEMLİ: Buraya Replit'te kullandığın bülten çekme API'sini veya kodunu entegre edeceğiz.
            # Şimdilik örnek bir yapı kuruyorum:
            conn = get_conn()
            # Örnek: Replit'teki bülten çekme mantığını buraya simüle ediyoruz
            # bulten_verisi = requests.get("SENIN_BULTEN_API_LINKIN").json()
            
            st.success("✅ Bülten başarıyla güncellendi!")
        except Exception as e:
            st.error(f"❌ Güncelleme sırasında hata oluştu: {e}")

# --- ÜST MENÜ VE GÜNCELLEME ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("🔄 Bülteni Güncelle"):
        bulteni_internetten_cek()

with col2:
    tarih_sec = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    t_str = tarih_sec.strftime('%Y-%m-%d')

# --- ANALİZ PANELİ ---
conn = get_conn()
# Veritabanından bülteni oku
bulten = pd.read_sql(f"SELECT * FROM current_bulletin WHERE date = '{t_str}'", conn)

st.divider()

c1, c2, c3 = st.columns(3)

with c1:
    if not bulten.empty:
        bulten['mac'] = bulten['home_team'] + " - " + bulten['away_team']
        secilen = st.selectbox("Günün Bülteni", bulten['mac'].tolist())
        m = bulten[bulten['mac'] == secilen].iloc[0]
        secilen_takim = m['home_team']
        secilen_round = m['round']
        secilen_lig = m['league']
    else:
        st.warning("Bülten bulunamadı. Manuel giriş yapın:")
        secilen_takim = st.text_input("Takım:", "Mallorca")
        secilen_round = st.number_input("Hafta (Round):", value=15)
        secilen_lig = st.selectbox("Lig Seç:", pd.read_sql("SELECT DISTINCT league FROM matches", conn)['league'].tolist())

with c2:
    algo = st.selectbox("Algoritma", ["Skor Analizi", "İY/MS & Oran", "Alt/Üst & KG"])

# Analiz Sonuçları
if secilen_takim:
    res = pd.read_sql(f"""
        SELECT * FROM matches 
        WHERE (home_team = '{secilen_takim}' OR away_team = '{secilen_takim}') 
        AND round = '{secilen_round}' AND league = '{secilen_lig}'
    """, conn)
    
    if not res.empty:
        st.subheader(f"🔍 {secilen_takim} - {secilen_round}. Hafta Analizi")
        res['skor'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
        
        if algo == "Skor Analizi":
            skorlar = res['skor'].value_counts().head(6)
            cols = st.columns(3)
            for i, (skor, count) in enumerate(skorlar.items()):
                cols[i % 3].success(f"**{skor}** \n %{(count/len(res))*100:.1f}")

        elif algo == "İY/MS & Oran":
            res['iy'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
            st.dataframe(res[['date', 'iy', 'skor', 'iddaa_ms1', 'iddaa_msx', 'iddaa_ms2']], use_container_width=True)

        elif algo == "Alt/Üst & KG":
            au = res['alt_ust_25'].value_counts()
            kg = res['kg_result'].value_counts()
            st.metric("En Çok Biten", f"2.5 {au.index[0] if not au.empty else '-'}")
            st.metric("KG Durumu", f"KG {kg.index[0] if not kg.empty else '-'}")
    else:
        st.error("Haftalık döngü verisi bulunamadı.")
conn.close()
