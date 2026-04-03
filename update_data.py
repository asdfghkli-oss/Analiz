import pandas as pd
import requests

def fetch_fbref_data():
    # FBref Güncel Fikstür Sayfası
    url = "https://fbref.com/en/matches/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print("🚀 FBref üzerinden güncel maçlar çekiliyor...")

    try:
        # Sayfayı indir
        response = requests.get(url, headers=headers, timeout=20)
        
        # HTML içindeki tabloları oku
        tables = pd.read_html(response.text)
        
        # Genellikle ilk tablo günün maçlarını içerir
        if tables:
            df_raw = tables[0]
            
            # Sütun isimlerini düzenleyelim (FBref standartlarına göre)
            # Genellikle: Date, League, Home, Score, Away gibi gelir
            all_matches = []
            
            for _, row in df_raw.iterrows():
                # Boş satırları ve başlık tekrarlarını atla
                if pd.isna(row.get('Home')) or row.get('Home') == 'Home':
                    continue
                    
                all_matches.append({
                    'Date': row.get('Date'),
                    'League': row.get('Competition'),
                    'HomeTeam': row.get('Home'),
                    'AwayTeam': row.get('Away')
                })

            if all_matches:
                df = pd.DataFrame(all_matches)
                df.to_csv("all_leagues_data.csv", index=False)
                print(f"✅ FBref BAŞARILI: {len(df)} maç kaydedildi.")
            else:
                print("⚠️ Tablo bulundu ama maç verisi ayıklanamadı.")
        else:
            print("❌ Sayfada maç tablosu bulunamadı.")
            
    except Exception as e:
        print(f"🛑 FBref Bağlantı Hatası: {e}")

if __name__ == "__main__":
    fetch_fbref_data()
