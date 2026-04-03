import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Otomatik Güncel Analiz Paneli")

DATA_FILE = "all_leagues_data.csv"

# Veri dosyası var mı kontrol et
if not os.path.exists(DATA_FILE):
    st.warning("⚠️ Veri dosyası henüz hazır değil. Lütfen GitHub Actions sekmesinden 'Run workflow' yapın.")
else:
    try:
        # Veriyi oku
        df = pd.read_csv(DATA_FILE)
        
        # --- SÜTUN İSİMLERİNİ STANDARTLAŞTIR (HATA ÖNLEYİCİ) ---
        # Tüm sütun isimlerini küçük harfe çevir ve boşlukları sil
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Gerekli sütunları bul (farklı isimlerde gelseler bile yakala)
        col_map = {
            'date': 'date',
            'roundnumber': 'round',
            'hometeam': 'home',
            'awayteam': 'away',
            'homescore': 'h_score',
            'awayscore': 'a_score',
            'league': 'league'
        }
        
        # Tarih formatını güvenli hale getir
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df = df.dropna(subset=['date'])
        
        # --- ARAYÜZ ---
        col1, col2 = st.columns(2)
        
        with col1:
            ligler = sorted(df['league'].unique()) if 'league' in df.columns else []
            secilen_lig = st.selectbox("1️⃣ Lig Seçin", ligler)
        
        with col2:
            bugun = pd.Timestamp.now().strftime('%Y-%m-%d')
            # Bugün ve sonrası maçlar (Bülten)
            bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
            
            if not bulten.empty:
                bulten['mac_adi'] = bulten['hometeam'] + " - " + bulten['awayteam']
                secilen_mac = st.selectbox("2️⃣ Bülten Seçin", bulten['mac_adi'].unique())
                m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
            else:
                st.warning("Bu ligde yakında maç yok.")
                m = None

        if m is not None:
            st.divider()
            st.subheader(f"📊 {secilen_mac} ({m['roundnumber']}. Hafta Analizi)")
            
            # ANALİZ: Aynı hafta döngüsündeki OYNANMIŞ maçlar
            gecmis = df[(df['league'] == secilen_lig) & 
                        (df['homescore'].notnull()) & 
                        (df['roundnumber'] == m['roundnumber'])].copy()
            
            if not gecmis.empty:
                gecmis['Sonuç'] = gecmis['homescore'].astype(int).astype(str) + "-" + gecmis['awayscore'].astype(int).astype(str)
                
                st.write(f"🔍 {m['roundnumber']}. Hafta Döngüsü Geçmiş Skorları:")
                
                # Tablo için sütunları düzelt
                tablo = gecmis[['date', 'hometeam', 'awayteam', 'Sonuç']]
                tablo.columns = ['Tarih', 'Ev Sahibi', 'Deplasman', 'Skor']
                st.table(tablo)
                
                # İstatistik
                en_cok = gecmis['Sonuç'].value_counts().idxmax()
                st.success(f"💡 Bu döngüde en sık biten skor: **{en_cok}**")
            else:
                st.info("Bu hafta döngüsüne ait geçmiş maç verisi henüz yok.")

    except Exception as e:
        st.error(f"⚠️ Bir hata oluştu: {e}")
        st.info("İpucu: GitHub Actions'ın dosyayı doğru oluşturduğundan emin olun.")
