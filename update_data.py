import pandas as pd
import requests
from datetime import datetime

def fetch_api_sports_data():
    # Bugünün tarihini al
    bugun = datetime.now().strftime('%Y-%m-%d')
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    # Senin RapidAPI Anahtarın
    headers = {
        "x-rapidapi-key": "3484137886mshefa3b568477dba7p10423fjsn346dc68691f0",
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    # Bugünün tüm maçlarını sorgula
    querystring = {"date": bugun}

    print(f"🚀 API-Sports üzerinden {bugun} maçları çekiliyor...")
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        if response.status_code == 200:
            data = response.json()
            all_matches = []
            
            for item in data.get('response', []):
                all_matches.append({
                    'Date': item['fixture']['date'],
                    'League': item['league']['name'],
                    'Country': item['league']['country'],
                    'HomeTeam': item['teams']['home']['name'],
                    'AwayTeam': item['teams']['away']['name'],
                    'Status': item['fixture']['status']['long']
                })
            
            if all_matches:
                df = pd.DataFrame(all_matches)
                # Saat dilimini temizle
                df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
                df.to_csv("all_leagues_data.csv", index=False)
                print(f"✅ {len(df)} maç başarıyla kaydedildi!")
            else:
                print("⚠️ Bugün için bülten boş döndü.")
        else:
            print(f"❌ API Hatası: {response.status_code}")
    except Exception as e:
        print(f"🛑 Bağlantı Hatası: {e}")

if __name__ == "__main__":
    fetch_api_sports_data()
