import requests
import pandas as pd

def fetch_all():
    # Aradığın 20+ ligin listesi (Buraya ekleme yapabilirsin)
    ligler = {
        "Süper Lig": "turkey-super-lig", "TFF 1. Lig": "turkey-tff-1-lig",
        "Premier League": "epl", "La Liga": "la-liga",
        "Serie A": "serie-a", "Bundesliga": "bundesliga",
        "Ligue 1": "ligue-1", "Eredivisie": "netherlands-eredivisie",
        "Portekiz": "portugal-primeira-liga", "Brezilya": "brazil-serie-a"
    }
    
    all_data = []
    for ad, kod in ligler.items():
        try:
            # 2025 sezonu hem bülteni hem geçmişi kapsar
            url = f"https://fixturedownload.com/feed/json/{kod}-2025"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                temp_df = pd.DataFrame(r.json())
                # SÜTUNLARI STANDARTLAŞTIR (Hataları önleyen altın kural)
                temp_df.columns = [str(c).lower().strip() for c in temp_df.columns]
                temp_df['league'] = ad
                all_data.append(temp_df)
        except:
            continue
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Dosyayı kaydet
        final_df.to_csv("all_leagues_data.csv", index=False)
        print("✅ 20+ Lig Başarıyla Veritabanına Eklendi!")

if __name__ == "__main__":
    fetch_all()
