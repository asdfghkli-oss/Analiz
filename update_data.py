import requests
import pandas as pd

def fetch_all():
    # Güncel ve geniş lig listesi
    ligler = {
        "Süper Lig": "turkey-super-lig",
        "Premier League": "epl",
        "La Liga": "la-liga",
        "Serie A": "serie-a",
        "Bundesliga": "bundesliga",
        "Ligue 1": "ligue-1",
        "Hollanda": "netherlands-eredivisie"
    }
    
    all_data = []
    for ad, kod in ligler.items():
        try:
            # 2025 sezonu hem geçmişi hem geleceği kapsar
            url = f"https://fixturedownload.com/feed/json/{kod}-2025"
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                temp_df = pd.DataFrame(r.json())
                # SÜTUNLARI STANDARTLAŞTIR: Hepsini küçük harf yap
                temp_df.columns = [c.lower().strip() for c in temp_df.columns]
                temp_df['league'] = ad
                all_data.append(temp_df)
        except:
            continue
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Veriyi CSV olarak kaydet
        final_df.to_csv("all_leagues_data.csv", index=False)
        print("Veri başarıyla güncellendi!")

if __name__ == "__main__":
    fetch_all()
