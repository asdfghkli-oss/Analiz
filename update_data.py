import pandas as pd

def fetch_pro_data():
    # 2024-2025 Sezonu Ana Ligler
    urls = {
        "Süper Lig": "https://www.football-data.co.uk/mmz4281/2425/T1.csv",
        "Premier League": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
        "La Liga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
        "Serie A": "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
        "Bundesliga": "https://www.football-data.co.uk/mmz4281/2425/D1.csv",
        "Ligue 1": "https://www.football-data.co.uk/mmz4281/2425/F1.csv",
        "Hollanda": "https://www.football-data.co.uk/mmz4281/2425/N1.csv",
        "Portekiz": "https://www.football-data.co.uk/mmz4281/2425/P1.csv",
        "Belçika": "https://www.football-data.co.uk/mmz4281/2425/B1.csv",
        "İskoçya": "https://www.football-data.co.uk/mmz4281/2425/SC0.csv"
    }
    
    all_leagues = []
    
    for name, url in urls.items():
        try:
            df = pd.read_csv(url)
            # FTHG: Maç Sonu Ev, FTAG: Maç Sonu Dep
            # HTHG: İlk Yarı Ev, HTAG: İlk Yarı Dep
            cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HTHG', 'HTAG']
            df = df[cols].copy()
            df['League'] = name
            df['Season'] = "2024-2025"
            all_leagues.append(df)
            print(f"✅ {name} yüklendi.")
        except Exception as e:
            print(f"❌ {name} hatası: {e}")
            
    if all_leagues:
        final_df = pd.concat(all_leagues, ignore_index=True)
        # Hafta hesaplama (Her takıma göre maç sırası)
        final_df = final_df.sort_values(by=['League', 'Date'])
        # Basit bir hafta ataması (Her ligde maç sayısına göre)
        final_df['Week'] = final_df.groupby('League').cumcount() // (len(final_df['HomeTeam'].unique()) // 2) + 1
        
        final_df.to_csv("all_leagues_data.csv", index=False)
        print("🚀 Gelişmiş Veritabanı Hazır!")

if __name__ == "__main__":
    fetch_pro_data()
