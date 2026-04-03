import pandas as pd
import time
import requests

def dev_arsiv_operasyonu():
    # Ülke ve Liglerin FBref ID kodları
    # Format: {Lig Adı: ID}
    ligler = {
        # Türkiye
        "TR Süper Lig": 26, "TR 1.Lig": 951,
        # İspanya
        "ES La Liga": 12, "ES Segunda": 17,
        # İngiltere
        "EN Premier": 9, "EN Champ": 10, "EN League 1": 15,
        # Almanya
        "DE Bundesliga": 20, "DE 2.Bund": 33, "DE 3.Liga": 35,
        # İtalya
        "IT Serie A": 11, "IT Serie B": 18,
        # Fransa
        "FR Ligue 1": 13, "FR Ligue 2": 60,
        # Brezilya
        "BR Serie A": 24, "BR Serie B": 38,
        # Portekiz
        "PT Primeira": 32,
        # Hollanda
        "NL Eredivisie": 23,
        # Belçika
        "BE Pro League": 37,
        # Arjantin (Baba lig eklendi)
        "AR Primera": 21
    }

    sezonlar = ["2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026"]
    tum_veriler = []

    headers = {"User-Agent": "Mozilla/5.0"}

    for lig_ad, lig_id in ligler.items():
        for sezon in sezonlar:
            try:
                # FBref standart link yapısı
                url = f"https://fbref.com/en/comps/{lig_id}/{sezon}/schedule/"
                print(f"📡 Çekiliyor: {lig_ad} | Sezon: {sezon}")
                
                # Sayfayı oku
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    tables = pd.read_html(response.text)
                    df = tables[0]
                    
                    # Sütunları standartlaştır (FBref bazen sütun adlarını değiştirir)
                    # İhtiyacımız olanlar: Hafta (Wk), Tarih, Ev, Skor, Deplasman
                    df = df[['Wk', 'Date', 'Home', 'Away', 'Score']].dropna(subset=['Home', 'Away'])
                    
                    df['League'] = lig_ad
                    df['Season'] = sezon
                    
                    tum_veriler.append(df)
                    print(f"✅ Alındı: {len(df)} maç.")
                
                # Site tarafından engellenmemek için bekleme süresi (Kritik!)
                time.sleep(3) 
                
            except Exception as e:
                print(f"⚠️ Atlandı: {lig_ad} {sezon} (Veri henüz yok veya link hatalı)")

    if tum_veriler:
        final_df = pd.concat(tum_veriler, ignore_index=True)
        # Dosyayı kaydet
        final_df.to_csv("all_leagues_data.csv", index=False)
        print(f"🚀 İŞLEM TAMAMLANDI! Toplam {len(final_df)} satır veri toplandı.")

if __name__ == "__main__":
    dev_arsiv_operasyonu()
