import requests
import pandas as pd
import os

def fetch_all():
    ligler = {
        "Super Lig": "turkey-super-lig",
        "Premier League": "epl",
        "La Liga": "la-liga",
        "Serie A": "serie-a",
        "Bundesliga": "bundesliga",
        "Ligue 1": "ligue-1",
        "Hollanda Eredivisie": "netherlands-eredivisie"
    }
    
    final_list = []
    
    for isim, kod in ligler.items():
        try:
            url = f"https://fixturedownload.com/feed/json/{kod}-2025"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                df = pd.DataFrame(data)
                
                # KRİTİK NOKTA: Sütun isimlerini zorla küçük harf yap ve boşlukları sil
                df.columns = [str(c).lower().replace(' ', '') for c in df.columns]
                
                # Eksik olabilecek sütunları zorla tanımla
                df['league'] = isim
                
                # Eğer 'roundnumber' yoksa 'round' kullan, o da yoksa 1 yap
                if 'roundnumber' not in df.columns:
                    if 'round' in df.columns:
                        df['roundnumber'] = df['round']
                    else:
                        df['roundnumber'] = 1
                
                final_list.append(df)
                print(f"✅ {isim} verisi hazır.")
        except Exception as e:
            print(f"❌ {isim} hatası: {e}")

    if final_list:
        full_df = pd.concat(final_list, ignore_index=True)
        # Dosyayı kaydet
        full_df.to_csv("all_leagues_data.csv", index=False)
        print("🚀 Dosya 'all_leagues_data.csv' adıyla başarıyla kaydedildi!")
    else:
        print("🛑 Hiç veri çekilemedi!")

if __name__ == "__main__":
    fetch_all()
