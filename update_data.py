import requests
import pandas as pd
from datetime import datetime

def fetch_combined_data():
    # 1. ARŞİV VERİSİ (Geçmiş Maçlar)
    arch_url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv" # Örnek Premier Lig
    try:
        archive_df = pd.read_csv(arch_url)
        archive_df['Status'] = 'Played'
    except:
        archive_df = pd.DataFrame()

    # 2. GÜNCEL BÜLTEN (Henüz Oynanmamış Maçlar)
    # FixtureDownload gibi kaynaklar gelecek maçları 'Date' ile verir
    bulletin_url = "https://fixturedownload.com/feed/json/epl-2024" 
    try:
        r = requests.get(bulletin_url)
        bulletin_df = pd.DataFrame(r.json())
        bulletin_df['Status'] = 'Fixture'
    except:
        bulletin_df = pd.DataFrame()

    # Verileri Birleştir ve Kaydet
    # (Burada sütun isimlerini 'Date', 'HomeTeam', 'AwayTeam' olarak standartlaştırıyoruz)
    combined_df = pd.concat([archive_df, bulletin_df], ignore_index=True)
    combined_df.to_csv("all_leagues_data.csv", index=False)
    print("✅ Arşiv ve Günlük Bülten Birleştirildi!")

if __name__ == "__main__":
    fetch_combined_data()
