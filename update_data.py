import pandas as pd
import requests
from datetime import datetime

def fetch_data():
    # Senin RapidAPI Anahtarın
    headers = {
        "x-rapidapi-key": "3484137886mshefa3b568477dba7p10423fjsn346dc68691f0",
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    # Bugünün tarihini al (Format: YYYY-MM-DD)
    bugun = datetime.now().strftime('%Y-%m-%d')
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"date": bugun}

    print(f"🚀 {bugun} tarihi için veri çekiliyor...")

    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', 0)
            print(f"📊 API'den gelen toplam maç sayısı: {results}")

            all_matches = []
            for item in data.get('response', []):
                all_matches.append({
                    'Date': item['fixture']['date'],
                    'League': item['league']['name'],
                    'Country': item['league']['country'],
                    'HomeTeam': item['teams']['home']['name'],
                    'AwayTeam': item['teams']['away']['name']
                })
            
            if all_matches:
                df = pd.DataFrame(all_matches)
                # UTC'den temizleme
                df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
                df.to_csv("all_leagues_data.csv", index=False)
                print(f"✅ DOSYA DOLDURULDU: {len(df)} maç kaydedildi.")
            else:
                print("⚠️ UYARI: API bağlantısı başarılı ama bugün için hiç maç dönmedi!")
        else:
            print(f"❌ API HATASI: Durum kodu {r.status_code}")
    except Exception as e:
        print(f"🛑 KRİTİK HATA: {e}")

if __name__ == "__main__":
    fetch_data()
