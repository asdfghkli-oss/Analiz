import pandas as pd

def fetch_pro_data():
    # Profesyonel liglerin doğrudan CSV linkleri (Örnek 5 tane, 20+ yapılabilir)
    urls = {
        "Premier League": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
        "Championship": "https://www.football-data.co.uk/mmz4281/2425/E1.csv",
        "La Liga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
        "Serie A": "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
        "Bundesliga": "https://www.football-data.co.uk/mmz4281/2425/D1.csv",
        "Ligue 1": "https://www.football-data.co.uk/mmz4281/2425/F1.csv",
        "Hollanda": "https://www.football-data.co.uk/mmz4281/2425/N1.csv",
        "Portekiz": "https://www.football-data.co.uk/mmz4281/2425/P1.csv",
        "Süper Lig": "https://www.football-data.co.uk/mmz4281/2425/T1.csv"
    }
    
    all_leagues = []
    
    for name, url in urls.items():
        try:
            df = pd.read_csv(url)
            # Sadece ihtiyacımız olan sütunları alalım (Tarih, Takımlar, Skorlar)
            df = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
            df['League'] = name
            all_leagues.append(df)
            print(f"✅ {name} verisi alındı.")
        except:
            print(f"❌ {name} kaynağına ulaşılamadı.")
            
    if all_leagues:
        final_df = pd.concat(all_leagues, ignore_index=True)
        final_df.to_csv("all_leagues_data.csv", index=False)
        print("🚀 Pro veritabanı hazır!")

if __name__ == "__main__":
    fetch_pro_data()
