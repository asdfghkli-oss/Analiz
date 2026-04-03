import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Analiz Kontrol", layout="wide")
st.title("🛠️ Veritabanı ve Sistem Kontrolü")

# 1. Dosya Kontrolü
if not os.path.exists('football.db'):
    st.error("❌ football.db dosyası GitHub deponuzda bulunamadı! Lütfen ana dizine yüklediğinizden emin olun.")
else:
    st.success("✅ football.db dosyası bulundu.")
    
    try:
        conn = sqlite3.connect('football.db')
        cursor = conn.cursor()
        
        # 2. Tablo İsimlerini Öğrenelim
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablolar = cursor.fetchall()
        st.write("📂 **Veritabanındaki Tablolar:**", tablolar)
        
        if tablolar:
            tablo_adi = tablolar[0][0] # İlk tabloyu otomatik seçer
            st.info(f"🔍 '{tablo_adi}' tablosu inceleniyor...")
            
            # 3. Sütun İsimlerini Öğrenelim
            cursor.execute(f"PRAGMA table_info({tablo_adi});")
            sutunlar = [column[1] for column in cursor.fetchall()]
            st.write("📊 **Sütun (Başlık) İsimleri:**", sutunlar)
            
            # 4. Örnek Veri Gösterimi
            df_ornek = pd.read_sql(f"SELECT * FROM {tablo_adi} LIMIT 3", conn)
            st.write("📝 **Tablodaki İlk 3 Satır:**", df_ornek)
            
        conn.close()
    except Exception as e:
        st.error(f"❌ Veritabanı okunurken bir hata oluştu: {e}")

st.divider()
st.write("💡 Eğer burada tablo isimlerini görüyorsan, bana o isimleri söyle. Kodu saniyeler içinde o isimlere göre düzelteyim.")
