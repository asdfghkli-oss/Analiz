import streamlit as st
import sqlite3
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Analiz Paneli", layout="wide")
st.title("🏟️ Yapay Zeka Destekli Analiz")

def get_conn():
    return sqlite3.connect('football.db', check_same_thread=False)

# 1. BÜLTEN ÇEKME (current_bulletin tablosu)
def get_bulten(tarih):
    conn = get_conn()
    try:
        # Sütun isimlerini senin db'ye göre eşitledim
        query = f"SELECT home_team, away_team, league, round FROM current_bulletin WHERE date = '{tarih}'"
        df = pd.read_sql(query, conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# 2. GEÇMİŞ ANALİZ (matches tablosu)
def get_analiz(takim, hafta, lig):
    conn = get_conn()
    try:
        # Senin db'deki sütunlara göre (round, league)
        query = f"""
        SELECT * FROM matches 
        WHERE (home_team = '{takim}' OR away_team = '{takim}') 
        AND round = '{hafta}' AND league = '{lig}'
        """
        df = pd.read_sql(query, conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# --- ARAYÜZ ---
c1, c2, c3 = st.columns(3)

with c1:
    tarih_sec = st.date_input("Tarih Seç", value=pd.to_datetime("today"))
    t_str = tarih_sec.strftime('%Y-%m-%d')

bulten = get_bulten(t_str)

with c2:
    if not bulten.empty:
        bulten['mac'] = bulten['home_team'] + " - " + bulten['away_team']
        secilen = st.selectbox("Günün Bülteni", bulten['mac'].tolist())
        m = bulten[bulten['mac'] == secilen].iloc[0]
    else:
        st.warning("Bülten bulunamadı.")
        secilen = None

with c3:
    algo = st.selectbox("Algoritma", ["Skor Analizi", "İY/MS & Oran", "Alt/Üst & KG"])

st.divider()

if secilen:
    res = get_analiz(m['home_team'], m['round'], m['league'])
    
    if not res.empty:
        st.subheader(f"🔍 {secilen} ({m['round']}. Hafta Analizi)")
        
        # Skorları birleştirme (home_score - away_score)
        res['skor'] = res['home_score'].astype(str) + "-" + res['away_score'].astype(str)
        
        if algo == "Skor Analizi":
            st.success("⚽ En Çok Çıkan Skorlar")
            skor_counts = res['skor'].value_counts().head(6)
            cols = st.columns(3)
            for i, (skor, count) in enumerate(skor_counts.items()):
                yuzde = (count / len(res)) * 100
                cols[i % 3].info(f"**{skor}** \n %{yuzde:.1f} ({count} Kez)")

        elif algo == "İY/MS & Oran":
            st.info("📊 Geçmiş Oranlar ve Sonuçlar")
            # İY skorunu birleştir
            res['iy'] = res['ht_home_score'].astype(str) + "-" + res['ht_away_score'].astype(str)
            st.dataframe(res[['date', 'iy', 'skor', 'iddaa_ms1', 'iddaa_msx', 'iddaa_ms2']], use_container_width=True)

        elif algo == "Alt/Üst & KG":
            c1, c2 = st.columns(2)
            # Alt/Üst 2.5
            au = res['alt_ust_25'].value_counts()
            c1.metric("2.5 Alt/Üst", f"{au.index[0] if not au.empty else '-'}")
            # KG Var/Yok
            kg = res['kg_result'].value_counts()
            c2.metric("KG Durumu", f"{kg.index[0] if not kg.empty else '-'}")
    else:
        st.error("Bu haftaya ait geçmiş veri bulunamadı.")
