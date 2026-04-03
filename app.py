import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# --- SIFIRDAN BÜLTEN ÇEKME FONKSİYONU ---
def bulteni_sifirdan_cek():
    with st.spinner('Güncel maçlar internetten toplanıyor...'):
        try:
            # Ücretsiz ve açık bir futbol bülten kaynağı (Örnektir)
            # Not: Bu URL örnek amaçlıdır, en stabil veri için hızlı bir API entegresi yapılmıştır.
            url = "https://fixturedownload.com/feed/json/epl-2025" # Örnek Premier Lig
            response = requests.get(url)
            data = response.json()
            
            conn = get_conn()
            cursor = conn.cursor()
            
            # Tabloyu temizle ve yeniden oluştur (Hata almamak için)
            cursor.execute("DROP TABLE IF EXISTS current_bulletin")
            cursor.execute("""
                CREATE TABLE current_bulletin (
                    date TEXT, 
                    home_team TEXT, 
                    away_team TEXT, 
                    league TEXT, 
                    round TEXT
                )
            """)
            
            # İnternetten gelen veriyi veritabanına yaz
            for match in data[:50]: # İlk 50 maçı örnek olarak alıyoruz
                cursor.execute("""
                    INSERT INTO current_bulletin (date, home_team, away_team, league, round) 
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    match['Date'][:10], # YYYY-MM-DD formatı
                    match['HomeTeam'], 
                    match['AwayTeam'], 
                    "Premier League", 
                    str(match['RoundNumber'])
                ))
            
            conn.commit()
            conn.close()
            st.success("✅ Güncel bülten çekildi ve veritabanına işlendi!")
            st.rerun() # Sayfayı yenile ki veriler gelsin
        except Exception as e:
            st.error(f"Bülten çekilirken hata oluştu: {e}")

# --- ÜST MENÜ ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🔄 Bülteni İnternetten Çek"):
        bulteni_sifirdan_cek()

with col2:
    tarih_sec = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    t_str = tarih_sec.strftime('%Y-%m-%d')

with col3:
    algo = st.selectbox("Algoritma", ["Skor Analizi", "İY/MS & Oran", "Alt/Üst & KG"])

st.divider()

# --- VERİ OKUMA ---
conn = get_conn()
try:
    bulten = pd.read_sql(f"SELECT * FROM current_bulletin WHERE date = '{t_str}'", conn)
except:
    bulten = pd.DataFrame()

# --- ANA EKRAN ---
if not bulten.empty:
    bulten['mac'] = bulten['home_team'] + " - " + bulten['away_team']
    secilen_mac = st.selectbox("Günün Bülteni", bulten['mac'].tolist())
    m = bulten[bulten['mac'] == secilen_mac].iloc[0]
    
    # Analiz Başlat Butonu
    if st.button("📊 ANALİZİ BAŞLAT"):
        # matches tablosundan geçmiş veriyi çek (Haftalık Döngü)
        res = pd.read_sql(f"""
            SELECT * FROM matches 
            WHERE (home_team = '{m['home_team']}' OR away_team = '{m['home_team']}') 
            AND round = '{m['round']}' AND league = '{m['league']}'
        """, conn)
        
        if not res.empty:
            st.subheader(f"🔍 {secilen_mac} - {m['round']}. Hafta Döngüsü")
            res['skor'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
            
            if algo == "Skor Analizi":
                skor_counts = res['skor'].value_counts().head(4)
                cols = st.columns(4)
                for i, (skor, count) in enumerate(skor_counts.items()):
                    cols[i].success(f"**{skor}** \n %{(count/len(res))*100:.1f}")
            
            elif algo == "İY/MS & Oran":
                res['iy'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
                st.dataframe(res[['date', 'iy', 'skor', 'iddaa_ms1', 'iddaa_ms2']], use_container_width=True)
        else:
            st.error("Bu maçın geçmişine dair aynı hafta/lig verisi bulunamadı.")
else:
    st.info("💡 Bugün için kayıtlı bülten yok. Lütfen 'Bülteni İnternetten Çek' butonuna basın.")
    # Manuel Giriş (Yedek)
    man_takim = st.text_input("Takım Adı:", "Real Madrid")
    man_round = st.number_input("Hafta:", value=1)
    if st.button("Manuel Analiz"):
        st.write("Analiz yapılıyor...")

conn.close()
