import streamlit as st
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# --- GELİŞMİŞ BÜLTEN ÇEKİCİ ---
def bulteni_guncelle():
    with st.spinner('Ligler taranıyor...'):
        try:
            ligler = {
                "Premier League": "epl", "Süper Lig": "turkey-super-lig",
                "La Liga": "la-liga", "Serie A": "serie-a",
                "Bundesliga": "bundesliga", "Ligue 1": "ligue-1"
            }
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS current_bulletin")
            cursor.execute("CREATE TABLE current_bulletin (date TEXT, home_team TEXT, away_team TEXT, league TEXT, round TEXT)")
            
            for lig_ad, lig_kod in ligler.items():
                r = requests.get(f"https://fixturedownload.com/feed/json/{lig_kod}-2025")
                if r.status_code == 200:
                    for match in r.json():
                        m_date = match.get('Date', '')[:10]
                        cursor.execute("INSERT INTO current_bulletin VALUES (?, ?, ?, ?, ?)", 
                                     (m_date, match['HomeTeam'], match['AwayTeam'], lig_ad, str(match['RoundNumber'])))
            conn.commit()
            conn.close()
            st.success("✅ Bülten Güncellendi!")
            st.rerun()
        except Exception as e:
            st.error(f"Hata: {e}")

# --- ARAYÜZ ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Bülteni İnternetten Çek"):
        bulteni_guncelle()
with col2:
    t_str = st.date_input("Tarih Seç", value=pd.to_datetime("today")).strftime('%Y-%m-%d')

st.divider()

# --- VERİ OKUMA ---
conn = get_conn()
try:
    bulten = pd.read_sql(f"SELECT * FROM current_bulletin WHERE date = '{t_str}'", conn)
except:
    bulten = pd.DataFrame()

if not bulten.empty:
    bulten['mac_gorunum'] = bulten['league'] + ": " + bulten['home_team'] + " - " + bulten['away_team']
    secilen_mac = st.selectbox("🎯 Maç Seçin", bulten['mac_gorunum'].tolist())
    m = bulten[bulten['mac_gorunum'] == secilen_mac].iloc[0]
    
    if st.button("🚀 İY/MS ANALİZİNİ BAŞLAT"):
        # ESNEK ARAMA: Lig ismi tam tutmasa da takım ismi ve hafta üzerinden ara
        query = f"""
            SELECT date, ht_home_score, ht_away_score, home_score, away_score 
            FROM matches 
            WHERE (home_team LIKE '%{m['home_team']}%' OR away_team LIKE '%{m['home_team']}%') 
            AND round = '{m['round']}'
        """
        res = pd.read_sql(query, conn)
        
        if not res.empty:
            st.subheader(f"📊 {m['home_team']} Analizi (Hafta: {m['round']})")
            res['İY'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
            res['MS'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
            
            # Sonuçları göster
            st.table(res[['date', 'İY', 'MS']])
            
            # En çok çıkan İY/MS
            res['İYMS'] = res['İY'] + " / " + res['MS']
            st.success(f"💡 Bu döngüdeki en yaygın sonuç: **{res['İYMS'].value_counts().idxmax()}**")
        else:
            st.error(f"Veritabanında {m['home_team']} için {m['round']}. haftaya ait geçmiş kayıt bulunamadı.")
else:
    st.info("💡 Bu tarihte maç bulunamadı. Lütfen 'Bülteni İnternetten Çek' butonuna basmayı veya tarihi değiştirmeyi deneyin.")

conn.close()
