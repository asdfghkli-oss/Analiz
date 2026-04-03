import requests
import pandas as pd

def fetch_all():
    # FBref'teki popüler 20+ ligin karşılıkları
    ligler = {
        "Süper Lig": "turkey-super-lig", "TFF 1. Lig": "turkey-tff-1-lig",
        "Premier League": "epl", "Championship": "england-championship",
        "La Liga": "la-liga", "La Liga 2": "spain-la-liga-2",
        "Serie A": "serie-a", "Serie B": "italy-serie-b",
        "Bundesliga": "bundesliga", "2. Bundesliga": "germany-2-bundesliga",
        "Ligue 1": "ligue-1", "Ligue 2": "france-ligue-2",
        "Eredivisie": "netherlands-eredivisie", "Portekiz Ligi": "portugal-primeira-liga",
        "Belçika Ligi": "belgium-pro-league", "Brezilya Seri A": "brazil-serie-a"
    }
    
    all_data = []
    for ad, kod in ligler.items():
        try:
            url = f"https://fixturedownload.com/feed/json/{kod}-2025"
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and r.json():
                temp_df = pd.DataFrame(r.json())
                # Sütun isimlerini zorla küçük harf yap (Hataları bitiren hamle)
                temp_df.columns = [str(c).lower().strip() for c in temp_df.columns]
                temp_df['league'] = ad
                all_data.append(temp_df)
        except:
            continue
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Dosyayı CSV olarak kaydet
        final_df.to_csv("all_leagues_data.csv", index=False)
        print("✅ Veri başarıyla güncellendi!")

if __name__ == "__main__":
    fetch_all()
