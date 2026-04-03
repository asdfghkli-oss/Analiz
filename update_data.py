import pandas as pd
import requests

def fetch_with_api():
    # Senin verdiğin özel API Key
    api_key = "2fb7b594f09acd4b3521ddf50fa227e9"
    headers = {'X-Auth-Token': api_key}
    
    # Premier Lig, La Liga, Bundesliga, Serie A, Ligue 1
    leagues = ['PL', 'PD', 'BL1', 'SA', 'FL1'] 
    all_matches = []

    for league in leagues:
        url = f"https://api.football-data.org/v4/competitions/{league}/matches"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                for m in data['matches']:
                    all_matches.append({
                        'Date': m['utcDate'], # Baş harfi büyük 'Date'
                        'League': data['competition']['name'],
                        'HomeTeam': m['homeTeam']['name'],
                        'AwayTeam': m['awayTeam']['name'],
                        'FTHG': m['score']['fullTime']['home'],
                        'FTAG': m['score']['fullTime']['away']
                    })
        except: continue

    if all_matches:
        df = pd.DataFrame(all_matches)
        # Tarih formatını temizle ve saat dilimini kaldır
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        df.to_csv("all_leagues_data.csv", index=False)
        print(f"✅ Bülten Başarıyla Güncellendi: {len(df)} maç.")

if __name__ == "__main__":
    fetch_with_api()
