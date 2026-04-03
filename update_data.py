import pandas as pd
import requests

def fetch_free_data():
    # API KEY GEREKTİRMEYEN AÇIK KAYNAK (Football Data JSON)
    # Örnek olarak İngiltere Premier Lig verisini çekiyoruz
    url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/11/90.json"
    
    print("🚀 Ücretsiz açık kaynak verisi çekiliyor...")
    
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            all_matches = []
            
            for item in data:
                all_matches.append({
                    'Date': item['match_date'],
                    'League': "Premier League",
                    'HomeTeam': item['home_team']['home_team_name'],
                    'AwayTeam': item['away_team']['away_team_name'],
                    'HomeScore': item['home_score'],
                    'AwayScore': item['away_score']
                })
            
            if all_matches:
                df = pd.DataFrame(all_matches)
                df.to_csv("all_leagues_data.csv", index=False)
                print(f"✅ BAŞARILI: {len(df)} maç açık kaynaktan çekildi.")
            else:
                print("⚠️ Veri boş döndü.")
        else:
            print(f"❌ Bağlantı Hatası: {r.status_code}")
    except Exception as e:
        print(f"🛑 Hata: {e}")

if __name__ == "__main__":
    fetch_free_data()
