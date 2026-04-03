import streamlit as st
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# --- TÜM LİGLERİ KAPSAYAN BÜLTEN ÇEKİCİ ---
def bulteni_guncelle():
    with st.spinner('Tüm dünya ligleri çekiliyor...'):
        try:
            # Geniş kapsamlı bülten kaynağı
            ligler = {
                "Süper Lig": "turkey-super-lig",
                "Premier League": "epl",
                "La Liga": "la-liga",
                "Serie A": "serie-a",
                "Bundesliga": "bundesliga",
                "Ligue 1": "ligue-1",
                "Eredivisie": "eredivisie"
            }
            
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS current_bulletin")
            cursor.execute("CREATE TABLE current_bulletin (date TEXT, home_team TEXT, away_team TEXT, league TEXT, round TEXT)")
            
            for lig_ad, lig_kod in ligler.items():
                url = f"https://fixturedownload.com/feed/json/{lig_kod}-2025"
                r = requests.get(url)
                if r.status_code == 200:
                    data = r.json()
                    for match in data:
                        m_date = match.get('Date', '')[:10]
                        cursor.execute("INSERT INTO current_bulletin VALUES (?, ?, ?, ?, ?)", 
                                     (m_date, match['HomeTeam'], match['AwayTeam'], lig_ad, str(match['RoundNumber'])))
            
            conn.commit()
            conn.close()
            st.success("✅ Tüm Ligler Güncellendi!")
            st.rerun()
        except Exception as e:
            st.error(f"Hata: {e}")

# --- ARAYÜZ ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Tüm Liglerin Bültenini Çek"):
        bulteni_guncelle()
with col2:
    tarih_sec = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    t_str = tarih_sec.strftime('%Y-%m-%d')

st.divider()

# --- VERİ OKUMA ---
conn = get_conn()
try:
    # Veritabanında hangi ligler ve maçlar varsa getir
    bulten = pd.read_sql(f"SELECT * FROM current_bulletin WHERE date = '{t_str}'", conn)
except:
    bulten = pd.DataFrame()

if not bulten.empty:
    # Lig bazlı gruplandırılmış liste
    bulten['mac_gorunum'] = bulten['league'] + ": " + bulten['home_team'] + " - " + bulten['away_team']
    secilen_mac = st.selectbox("🎯 Maç Seçin (Lig: Ev Sahibi - Deplasman)", bulten['mac_gorunum'].tolist())
    m = bulten[bulten['mac_gorunum'] == secilen_mac].iloc[0]
    
    if st.button("🚀 İY/MS ANALİZİNİ BAŞLAT"):
        # Geçmiş Döngü Analizi
        res = pd.read_sql(f"""
            SELECT date, ht_home_score, ht_away_score, home_score, away_score 
            FROM matches 
            WHERE (home_team = '{m['home_team']}' OR away_team = '{m['home_team']}') 
            AND round = '{m['round']}' AND league = '{m['league']}'
        """, conn)
        
        if not res.empty:
            st.subheader(f"📊 {m['home_team']} - {m['away_team']} ({m['round']}. Hafta)")
            
            res['İY'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
            res['MS'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
            
            # Sonuç Tablosu
            st.table(res[['date', 'İY', 'MS']])
            
            # Özet İstatistik
            res['İYMS'] = res['İY'] + " / " + res['MS']
            top_sonuc = res['İYMS'].value_counts().idxmax()
            st.info(f"💡 Bu döngüde en çok çıkan sonuç: **{top_sonuc}**")
        else:
            st.error("Bu lig ve hafta için geçmiş döngü verisi bulunamadı.")
else:
    st.warning("⚠️ Seçilen tarihte bülten yok. Lütfen 'Tüm Liglerin Bültenini Çek' butonuna basın.")

conn.close()
