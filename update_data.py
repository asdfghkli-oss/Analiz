import sqlite3
import pandas as pd
import requests

def db_guncelle():
    db_yolu = "football.db"
    conn = sqlite3.connect(db_yolu)
    cursor = conn.cursor()

    print("📡 Veritabanı bağlantısı kuruldu. Güncel bülten taranıyor...")
    
    # Buraya FBref veya kendi veri kaynağının API/Scraper kodunu ekleyebilirsin.
    # Örnek: Mevcut matches tablosuna yeni verileri INSERT eden bir mantık.
    
    # Şimdilik mevcut tabloların sağlığını kontrol edelim
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Mevcut Tablolar: {tables}")
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    conn.close()
    print("🚀 Güncelleme işlemi tamamlandı.")

if __name__ == "__main__":
    db_guncelle()
