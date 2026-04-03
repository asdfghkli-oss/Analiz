import pandas as pd
import requests

def fetch_all():
    # Güncel bülten veren güvenilir ligler
    bulletin_leagues = {
        "Süper Lig": "turkey-super-lig", 
        "Premier League": "epl",
        "La Liga": "la-liga", 
        "Serie A": "serie-a", 
        "Bundesliga": "bundesliga",
        "Ligue 1": "france-ligue-1",
        "Eredivisie": "netherlands-eredivisie"
    }
    
    all_rows = []
    for name, code in bulletin_leagues.items():
        try:
            # 2025/26 sezonu için güncel bülten linki
            url = f"https://fixturedownload.com/feed/json/{code}-2025"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                for match in data:
                    all_rows.append({
                        'Date': match.get('Date'),
                        'League': name,
                        'HomeTeam': match.get('HomeTeam'),
                        'AwayTeam': match.get('AwayTeam'),
                        'FTHG': match.get('HomeTeamScore'),
                        'FTAG': match.get('AwayTeamScore'),
                        'Status': 'Fixture' if match.get('HomeTeamScore') is None else 'Played'
                    })
        except: 
            continue

    if all_rows:
        df = pd.DataFrame(all_rows)
        # HATA ÇÖZÜMÜ: Tarih formatını ISO8601 olarak zorla (ValueError engelleyici)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True).dt.tz_localize(None)
        df = df.dropna(subset=['Date']) # Geçersiz tarihleri sil
        df.to_csv("all_leagues_data.csv", index=False)
        print("✅ Bülten başarıyla hazırlandı!")

if __name__ == "__main__":
    fetch_all()
