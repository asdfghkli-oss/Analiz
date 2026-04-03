import streamlit as st
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="Analiz Paneli", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# --- SIFIRDAN BÜLTEN ÇEKME (STABİL KAYNAK) ---
def bulteni_guncelle():
    with st.spinner('Güncel maçlar internetten çekiliyor...'):
        try:
            # Daha stabil bir API/JSON kaynağı
            url = "https://fixturedownload.com/feed/json/epl-2025" 
            r = requests.get(url)
            data = r.json()
            
            conn = get_conn()
            cursor = conn.cursor()
            
            cursor.execute("DROP TABLE IF EXISTS current_bulletin")
            cursor.execute("CREATE TABLE current_bulletin (date TEXT, home_team TEXT, away_team TEXT, league TEXT, round TEXT)")
            
            for match in data:
                # 'Date' yerine 'Date' anahtarını kontrol ederek alıyoruz
                match_date = match.get('Date', '2026-04-03')[:10]
                cursor.execute("INSERT INTO current_bulletin VALUES (?, ?, ?, ?, ?)", 
                             (match_date, match['HomeTeam'], match['AwayTeam'], "Premier League", str(match['RoundNumber'])))
            
            conn.commit()
            conn.close()
            st.success("✅ Bülten Güncellendi!")
            st.rerun()
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 Bülteni İnternetten Çek"):
        bulteni_guncelle()

with col2:
    tarih_sec = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    t_str = tarih_sec.strftime('%Y-%m-%d')

st.divider()

# --- VERİ OKUMA ---
conn = get_conn()
try:
    bulten = pd.read_sql(f"SELECT * FROM current_bulletin WHERE date = '{t_str}'", conn)
except:
    bulten = pd.DataFrame()

if not bulten.empty:
    bulten['mac'] = bulten['home_team'] + " - " + bulten['away_team']
    secilen_mac = st.selectbox("🎯 Bir Maç Seçin", bulten['mac'].tolist())
    m = bulten[bulten['mac'] == secilen_mac].iloc[0]
    
    if st.button("🚀 ANALİZİ BAŞLAT"):
        # Haftalık Döngü Analizi (matches tablosundan)
        res = pd.read_sql(f"""
            SELECT date, ht_home_score, ht_away_score, home_score, away_score 
            FROM matches 
            WHERE (home_team = '{m['home_team']}' OR away_team = '{m['home_team']}') 
            AND round = '{m['round']}' AND league = '{m['league']}'
        """, conn)
        
        if not res.empty:
            st.subheader(f"📊 {secilen_mac} (Hafta: {m['round']})")
            
            # Skor birleştirme
            res['İY'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
            res['MS'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
            res['İY/MS'] = res['İY'] + " / " + res['MS']
            
            # Tablo Gösterimi
            st.write("### Geçmiş Döngüdeki İY/MS Sonuçları")
            st.table(res[['date', 'İY', 'MS']])
            
            # İstatistik Kutucukları
            iy_ms_counts = res['İY/MS'].value_counts().head(3)
            cols = st.columns(3)
            for i, (sonuc, count) in enumerate(iy_ms_counts.items()):
                yuzde = (count / len(res)) * 100
                cols[i].metric(f"En Çok Çıkan {i+1}", sonuc, f"%{yuzde:.0f}")
        else:
            st.error("Bu maçın haftalık döngüsüne ait geçmiş veri bulunamadı.")
else:
    st.info("💡 Seçilen tarihte bülten yok. Lütfen yukarıdaki butondan bülteni çekin.")

conn.close()
