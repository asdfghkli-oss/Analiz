import streamlit as st
import sqlite3
import pandas as pd

# Sayfa Yapılandırması
st.set_page_config(page_title="Pro Analiz Paneli", layout="wide")

def get_connection():
    return sqlite3.connect('football.db', check_same_thread=False)

# 1. VERİ ÇEKME FONKSİYONLARI
def bulten_getir(tarih):
    conn = get_connection()
    # Seçilen tarihteki maçları veritabanından çeker
    query = f"SELECT home_team, away_team, league, week FROM matches WHERE date = '{tarih}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def gecmis_verileri_sorgula(takim, hafta, lig):
    conn = get_connection()
    # Son 5 yıl, aynı lig, aynı hafta verisi
    query = f"""
    SELECT * FROM matches 
    WHERE (home_team = '{takim}' OR away_team = '{takim}') 
    AND week = {hafta} AND league = '{lig}'
    ORDER BY date DESC LIMIT 50
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- ARAYÜZ BAŞLANGICI ---
st.title("🏟️ Yapay Zeka Destekli Analiz")

# Üst Filtreler
col1, col2, col3 = st.columns(3)

with col1:
    secilen_tarih = st.date_input("Tarih Seç", value=pd.to_datetime("today"))

# Bülteni Yükle
df_bulten = bulten_getir(secilen_tarih.strftime('%Y-%m-%d'))

with col2:
    if not df_bulten.empty:
        df_bulten['mac_adi'] = df_bulten['home_team'] + " - " + df_bulten['away_team']
        secilen_mac = st.selectbox("Günün Bülteni", df_bulten['mac_adi'].tolist())
        # Seçilen maçın bilgilerini ayıkla
        mac_info = df_bulten[df_bulten['mac_adi'] == secilen_mac].iloc[0]
    else:
        st.warning("Bu tarihte bülten bulunamadı.")
        secilen_mac = None

with col3:
    algoritma = st.selectbox("Algoritma Seçin", 
                            ["İY/MS Algoritması (Sürpriz)", "Skor Algoritması", "Toplam Gol Algoritması", "KG Var (İki Yarı)"])

st.divider()

if secilen_mac:
    # Analiz Başlat
    hist_data = gecmis_verileri_sorgula(mac_info['home_team'], mac_info['week'], mac_info['league'])
    
    if not hist_data.empty:
        st.subheader(f"🔍 {secilen_mac} Analizi ({mac_info['week']}. Hafta Döngüsü)")
        
        # --- ALGORİTMA MANTIKLARI ---
        
        if algoritma == "İY/MS Algoritması (Sürpriz)":
            st.info("🎯 İY/MS Sürpriz Sonuçlar (2/1, 1/2, 1/0, 2/0)")
            surprizler = hist_data[hist_data['iy_ms'].isin(['2/1', '1/2', '1/0', '2/0'])]
            if not surprizler.empty:
                st.write(surprizler[['date', 'home_team', 'away_team', 'iy_skor', 'ms_skor', 'iy_ms']])
            else:
                st.write("Geçmişte bu hafta sürpriz sonuçlanmamış.")

        elif algoritma == "Skor Algoritması":
            st.success("⚽ En Çok Çıkan Skorlar")
            skor_counts = hist_data['ms_skor'].value_counts().head(4)
            c1, c2, c3, c4 = st.columns(4)
            cols = [c1, c2, c3, c4]
            for i, (skor, count) in enumerate(skor_counts.items()):
                yuzde = (count / len(hist_data)) * 100
                cols[i].metric(label=f"Skor: {skor}", value=f"{count} Kere", delta=f"%{yuzde:.1f}")

        elif algoritma == "Toplam Gol Algoritması":
            st.warning("🥅 Toplam Gol Dağılımı")
            # 2-3, 4-5, 6+ Gruplama
            hist_data['gol_grubu'] = pd.cut(hist_data['toplam_gol'], bins=[-1, 1, 3, 5, 100], labels=['0-1', '2-3', '4-5', '6+'])
            gol_counts = hist_data['gol_grubu'].value_counts()
            st.bar_chart(gol_counts)

        elif algoritma == "KG Var (İki Yarı)":
            st.error("🔄 Her İki Yarıda Gol Var Analizi")
            iki_yari_gol = hist_data[(hist_data['iy_toplam_gol'] > 0) & (hist_data['ikinci_yari_gol'] > 0)]
            oran = (len(iki_yari_gol) / len(hist_data)) * 100
            st.metric("İki Yarıda da Gol Olma Olasılığı", f"%{oran:.1f}", f"{len(iki_yari_gol)} Maç")

    else:
        st.error("Seçili takımın geçmiş yıllarda bu haftasına ait veri bulunamadı.")
