import pandas as pd
import time
import requests
from datetime import datetime, timedelta

def tum_dunya_son_ay_cek():
    # FBref'in son maçlar/fikstürler ana sayfası (Tüm ligler buradadır)
    url = "https://fbref.com/en/matches/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    print("🌐 Tüm dünya son 1 ay verisi taranıyor... (Bu biraz sürebilir)")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            # Sayfadaki tüm tabloları çek (Genelde ilk tablo ana fikstürdür)
            tables = pd.read_html(response.text)
            df = tables[0]
            
            # Sütunları temizle ve standartlaştır
            # FBref bu sayfada genelde: Wk, Day, Date, Time, Home, Score, Away, Attendance, Venue, Referee, Comp yazar.
            df = df.dropna(subset=['Home', 'Away', 'Comp']) # Boş satırları ve ligsiz maçları at
            
            # Sütun isimlerini temizle (Görünmez boşlukları sil)
            df.columns = [str(c).strip() for c in df.columns]
            
            # Tarih filtresi (Sadece son 30 gün)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            bir_ay_once = datetime.now() - timedelta(days=30)
            df = df[df['Date'] >= bir_ay_once]
            
            # Tarihi geri metne çevir
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            # Dosyayı kaydet
            df.to_csv("all_leagues_data.csv", index=False)
            
            print(f"✅ İŞLEM TAMAM! Toplam {len(df)} maç ve onlarca farklı lig bulundu.")
            print(f"📋 Sütunlar: {list(df.columns)}")
        else:
            print(f"❌ Siteye erişilemedi! Hata Kodu: {response.status_code}")
            
    except Exception as e:
        print(f"🛑 Kritik Hata: {e}")

if __name__ == "__main__":
    tum_dunya_son_ay_cek()
