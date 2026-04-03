import requests
import pandas as pd

def fetch_data():
    # 20+ LİGLİK GENİŞ LİSTE
    ligler = {
        "Süper Lig": "turkey-super-lig",
        "TFF 1. Lig": "turkey-tff-1-lig",
        "Premier League": "epl",
        "Championship": "england-championship",
        "La Liga": "la-liga",
        "La Liga 2": "spain-la-liga-2",
        "Serie A": "serie-a",
        "Serie B": "italy-serie-b",
        "Bundesliga": "bundesliga",
        "Bundesliga 2": "germany-2-bundesliga",
        "Ligue 1": "ligue-1",
        "Ligue 2": "france-ligue-2",
        "Eredivisie": "netherlands-eredivisie",
        "Eerste Divisie": "netherlands-eerste-divisie",
        "Primeira Liga": "portugal-primeira-liga",
        "Pro League": "belgium-pro-league",
        "Premiership": "scotland-premiership",
        "Super League": "switzerland-super-league",
        "Bundesliga (AT)": "austria-bundesliga",
        "Superliga": "denmark-superliga",
        "Eliteserien": "norway-eliteserien",
        "Allsvenskan": "sweden-allsvenskan",
        "Serie A (BR)": "brazil-serie-a"
    }
    
    all_results = []
    
    for isim, kod in ligler.items():
        try:
            # 2025/26 Sezonu verisi
            url = f"https://fixturedownload.com/feed/json/{kod}-2025"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data:
                    df = pd.DataFrame(data)
                    # SÜTUNLARI STANDARTLAŞTIR (Hataları önleyen kısım)
                    df.columns = [c.lower().strip() for c in df.columns]
                    df['league'] = isim
                    all_results.append(df)
                    print(f"✅ {isim} yüklendi.")
        except:
            print(f"❌ {isim} çekilemedi.")
            
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        # Kayıt öncesi son temizlik
        final_df.to_csv("all_leagues_data.csv", index=False)
        print(f"🚀 Toplam {len(ligler)} ligden veri toplandı!")

if __name__ == "__main__":
    fetch_data()
