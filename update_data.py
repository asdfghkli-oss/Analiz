import pandas as pd
import requests
from datetime import datetime

def fetch_sofascore_data():
    # Bugünün tarihini al (YYYY-MM-DD formatında)
    bugun = datetime.now().strftime('%Y-%m-%d')
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{bugun}"
    
    headers = {
        "x-rapidapi-key": "3484137886mshefa3b568477dba7p10423fjsn346dc68691f0",
        "x-rapidapi-host": "sportapi7.p.rapidapi.com"
    }

    print(f"🚀 {bugun} tarihli tüm maçlar çekiliyor...")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            all_matches = []
            
            for event in data.get('events', []):
                all_matches.append({
                    'Date': datetime.fromtimestamp(event.get('startTimestamp')).strftime('%Y-%m-%d %H:%M'),
                    'League': event.get('tournament', {}).get('name'),
                    'HomeTeam': event.get('homeTeam', {}).get('name'),
                    'AwayTeam': event.get('awayTeam', {}).get('name'),
                    'HomeScore': event.get('homeScore', {}).get('current'),
                    'AwayScore': event.get('awayScore', {}).get('current')
                })
            
            if all_matches:
                df = pd.DataFrame(all_matches)
                # Streamlit'in okuması için kaydet
                df.to_csv("all_leagues_data.csv", index=False)
                print(f"✅ {len(df)} maç başarıyla kaydedildi!")
            else:
                print("⚠️ Bugün için maç bulunamadı.")
        else:
            print(f"❌ API Hatası: {response.status_code}")
    except Exception as e:
        print(f"🛑 Bağlantı Hatası: {e}")

if __name__ == "__main__":
    fetch_sofascore_data()
