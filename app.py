import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("🏟️ Akıllı Analiz Paneli")

DATA_FILE = "all_leagues_data.csv"

if not os.path.exists(DATA_FILE):
    st.warning("⚠️ Veri dosyası henüz oluşturulmadı. GitHub Actions'ın bitmesini bekleyin.")
else:
    try:
        df = pd.read_csv(DATA_FILE)
        
        # --- AKILLI SÜTUN TANIMA ---
        # Tüm başlıkları küçük harfe çevir ve temizle
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Kritik sütunları bulmak için eşleşme sözlüğü
        possible_cols = {
            'date': ['date', 'tarih', 'match_date', 'utcdate'],
            'home': ['hometeam', 'home', 'ev sahibi', 'team_1'],
            'away': ['awayteam', 'away', 'deplasman', 'team_2'],
            'h_score': ['homescore', 'home_score', 'ms1', 'iy1'],
            'a_score': ['awayscore', 'away_score', 'ms2', 'iy2'],
            'round': ['roundnumber', 'round', 'hafta', 'matchday'],
            'league': ['league', 'lig', 'competition']
        }
        
        # Sütunları yeniden adlandır
        new_cols = {}
        for key, aliases in possible_cols.items():
            for col in df.columns:
                if col in aliases:
                    new_cols[col] = key
        df = df.rename(columns=new_cols)

        # Eksik sütun kontrolü
        required = ['date', 'home', 'away', 'league']
        missing = [r for r in required if r not in df.columns]
        
        if missing:
            st.error(f"Dosyada şu bilgiler eksik: {missing}")
        else:
            # Tarih düzenleme
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
            
            col1, col2 = st.columns(2)
            with col1:
                ligler = sorted(df['league'].unique())
                secilen_lig = st.selectbox("1️⃣ Lig Seçin", ligler)
            
            with col2:
                bugun = pd.Timestamp.now().normalize()
                bulten = df[(df['league'] == secilen_lig) & (df['date'] >= bugun)].copy()
                
                if not bulten.empty:
                    bulten['mac_adi'] = bulten['home'] + " - " + bulten['away']
                    secilen_mac = st.selectbox("2️⃣ Maç Seçin", bulten['mac_adi'].unique())
                    m = bulten[bulten['mac_adi'] == secilen_mac].iloc[0]
                else:
                    st.warning("Yakın tarihte maç bulunamadı.")
                    m = None

            if m is not None:
                st.divider()
                st.subheader(f"📊 {secilen_mac} ({m['round']}. Hafta Analizi)")
                
                # GEÇMİŞ ANALİZİ
                # Aynı haftadaki oynanmış maçları bul
                gecmis = df[(df['league'] == secilen_lig) & 
                            (df['h_score'].notnull()) & 
                            (df['round'] == m['round'])].copy()
                
                if not gecmis.empty:
                    gecmis['Sonuç'] = gecmis['h_score'].astype(int).astype(str) + "-" + gecmis['a_score'].astype(int).astype(str)
                    
                    st.write(f"🔍 {m['round']}. Hafta Döngüsü Geçmişi:")
                    tablo = gecmis[['date_str', 'home', 'away', 'Sonuç']]
                    tablo.columns = ['Tarih', 'Ev Sahibi', 'Deplasman', 'Skor']
                    st.table(tablo)
                    
                    en_cok = gecmis['Sonuç'].value_counts().idxmax()
                    st.success(f"💡 Bu döngüde en sık görülen skor: **{en_cok}**")
                else:
                    st.info("Bu hafta döngüsüne ait geçmiş veri bulunamadı.")

    except Exception as e:
        st.error(f"Sistemsel bir hata oluştu: {e}")
