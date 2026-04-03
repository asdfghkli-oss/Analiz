import requests
import pandas as pd

def fetch_all():
    ligler = {
        "Süper Lig": "turkey-super-lig",
        "Premier League": "epl",
        "La Liga": "la-liga",
        "Serie A": "serie-a",
        "Bundesliga": "bundesliga",
        "Ligue 1": "ligue-1"
    }
    
    all_data = []
    for ad, kod in ligler.items():
        try:
            url = f"https://fixturedownload.com/feed/json/{kod}-2025"
            r = requests.get(url)
            if r.status_code == 200:
                temp_df = pd.DataFrame(r.json())
                temp_df['League'] = ad
                all_data.append(temp_df)
        except:
            continue
            
    if all_data:
        final_df = pd.concat(all_data)
        final_df.to_csv("all_leagues_data.csv", index=False)
        print("Veri başarıyla güncellendi!")

if __name__ == "__main__":
    fetch_all()
