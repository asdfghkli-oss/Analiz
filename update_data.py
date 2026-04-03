import sqlite3

def check_db_integrity():
    conn = sqlite3.connect("football.db")
    cursor = conn.cursor()
    
    # Tablo ve sütun yapısını doğrula
    try:
        cursor.execute("SELECT * FROM matches LIMIT 1")
        columns = [description[0] for description in cursor.description]
        print(f"✅ Veritabanı Aktif. Sütunlar: {columns}")
    except Exception as e:
        print(f"❌ Veritabanı Hatası: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_integrity()
