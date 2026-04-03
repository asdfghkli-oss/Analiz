import pandas as pd
import requests

def fetch_live_bulletin():
    # Günlük bülteni en hızlı güncelleyen ligler
    leagues = {
        "Süper Lig": "turkey-super-lig", 
        "Premier League": "epl",
        "La Liga": "la-liga", 
        "Serie A": "serie-a", 
        "Bundesliga": "bundesliga",
        "Ligue 1": "france-ligue-1",
        "Eredivisie": "netherlands-eredivisie",
        "Portekiz": "portugal-primeira-liga"
    }
    
    all_data = []
    for name, code in leagues.items():
        try:
            # 2025-2026 Güncel Sezon Bülteni
            url = f"https://fixturedownload.com/feed/json/{code}-2025"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data:
                    for m in data:
                        all_data.append({
                            'Date': m.get('Date'),
                            'League': name,
                            'HomeTeam': m.get('HomeTeam'),
                            'AwayTeam': m.get('AwayTeam'),
                            'FTHG': m.get('HomeTeamScore'), 
                            'FTAG': m.get('AwayTeamScore')
                        })
                    print(f"✅ {name} verisi alındı.")
        except Exception as e: 
            print(f"❌ {name} hatası: {e}")
            continue

    if all_data:
        df = pd.DataFrame(all_data)
        # Tarih formatını temizle (ISO 8601 uyumlu)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True).dt.tz_localize(None)
        df = df.dropna(subset=['Date'])
        df.to_csv("all_leagues_data.csv", index=False)
        print(f"🚀 Toplam {len(df)} maç kaydedildi!")
    else:
        print("🛑 HATA: Hiçbir veri çekilemedi!")

if __name__ == "__main__":
    fetch_live_bulletin()
