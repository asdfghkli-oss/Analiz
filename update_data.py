import pandas as pd
import requests

def fetch_all():
    # 1. BÜLTEN VERİSİ (Gelecek Maçlar)
    bulletin_leagues = {
        "Süper Lig": "turkey-super-lig", "Premier League": "epl",
        "La Liga": "la-liga", "Serie A": "serie-a", "Bundesliga": "bundesliga"
    }
    
    all_rows = []
    for name, code in bulletin_leagues.items():
        try:
            url = f"https://fixturedownload.com/feed/json/{code}-2025"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for match in data:
                    all_rows.append({
                        'Date': match.get('Date'),
                        'League': name,
                        'HomeTeam': match.get('HomeTeam'),
                        'AwayTeam': match.get('AwayTeam'),
                        'FTHG': match.get('HomeTeamScore'),
                        'FTAG': match.get('AwayTeamScore')
                    })
        except: continue

    df = pd.DataFrame(all_rows)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    df.to_csv("all_leagues_data.csv", index=False)
    print("✅ Bülten ve Arşiv Güncellendi!")

if __name__ == "__main__":
    fetch_all()
