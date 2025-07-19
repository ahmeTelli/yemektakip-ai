import sqlite3

DB_PATH = "restoran.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

def setup_tables():
    c.execute("""
    CREATE TABLE IF NOT EXISTS masalar (
        masa_id INTEGER PRIMARY KEY,
        aktif INTEGER DEFAULT 0,
        toplam_tutar REAL DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS yemekler (
        yemek_id INTEGER PRIMARY KEY,
        isim TEXT,
        fiyat REAL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS siparisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        masa_id INTEGER,
        yemek_id INTEGER,
        eklenme_zamani DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS garsonlar (
        garson_id INTEGER PRIMARY KEY,
        isim TEXT,
        puan INTEGER DEFAULT 0,
        aktif_masa INTEGER
    )
    """)
    conn.commit()
    yemekleri_ekle()
    garsonlari_ekle()
import random

def garson_ata(masa_id):

    c.execute("SELECT garson_id FROM garsonlar WHERE aktif_masa IS NULL")
    bos_garsonlar = [row[0] for row in c.fetchall()]
    if not bos_garsonlar:
        c.execute("SELECT garson_id FROM garsonlar")
        tum_garsonlar = [row[0] for row in c.fetchall()]
        secilen = random.choice(tum_garsonlar)
    else:
        secilen = random.choice(bos_garsonlar)

    c.execute("UPDATE garsonlar SET aktif_masa=? WHERE garson_id=?", (masa_id, secilen))
    conn.commit()
    return secilen  

def yemekleri_ekle():
    yemekler = [
        (0, "arnavutcigeri", 110),
        (1, "ayran", 25),
        (2, "domatescorbasi", 60),
        (3, "ezogelincorbasi", 65),
        (4, "karniyarik", 120),
        (5, "kola", 35),

    ]
    c.executemany("INSERT OR IGNORE INTO yemekler VALUES (?, ?, ?)", yemekler)
    conn.commit()


def garsonlari_ekle():
    garsonlar = [
        (1, "Ahmet", 75, None, 2), 
        (2, "Burcu", 82, None, 4)
    ]
    c.executemany("INSERT OR IGNORE INTO garsonlar VALUES (?, ?, ?, ?, ?)", garsonlar)
    conn.commit()

def masa_ac(masa_id):
    c.execute("INSERT OR IGNORE INTO masalar (masa_id, aktif, toplam_tutar) VALUES (?, 1, 0)", (masa_id,))
    c.execute("UPDATE masalar SET aktif=1, toplam_tutar=0 WHERE masa_id=?", (masa_id,))
    c.execute("DELETE FROM siparisler WHERE masa_id=?", (masa_id,))
    conn.commit()

def siparis_ekle(masa_id, yemek_id):
    c.execute("SELECT 1 FROM siparisler WHERE masa_id=? AND yemek_id=?", (masa_id, yemek_id))
    if not c.fetchone():
        c.execute("INSERT INTO siparisler (masa_id, yemek_id) VALUES (?, ?)", (masa_id, yemek_id))
        c.execute("SELECT fiyat FROM yemekler WHERE yemek_id=?", (yemek_id,))
        fiyat = c.fetchone()[0]
        c.execute("UPDATE masalar SET toplam_tutar = toplam_tutar + ? WHERE masa_id=?", (fiyat, masa_id))
        conn.commit()

def masa_bosalt(masa_id):
    c.execute("DELETE FROM siparisler WHERE masa_id=?", (masa_id,))
    c.execute("UPDATE masalar SET aktif=0, toplam_tutar=0 WHERE masa_id=?", (masa_id,))
    c.execute("UPDATE garsonlar SET aktif_masa=NULL WHERE aktif_masa=?", (masa_id,))
    conn.commit()

def toplam_tutar_getir(masa_id):
    c.execute("SELECT toplam_tutar FROM masalar WHERE masa_id=?", (masa_id,))
    result = c.fetchone()
    return result[0] if result else 0

def garson_ceza_ver(garson_id, puan_dusur=10):
    c.execute("UPDATE garsonlar SET puan = puan - ? WHERE garson_id=?", (puan_dusur, garson_id))
    conn.commit()

def rapor_verilerini_getir():

    c.execute("""
        SELECT masalar.masa_id, yemekler.isim, COUNT(*), DATE(siparisler.eklenme_zamani), 
        (SELECT isim FROM garsonlar WHERE aktif_masa=masalar.masa_id LIMIT 1)
        FROM siparisler
        JOIN masalar ON siparisler.masa_id=masalar.masa_id
        JOIN yemekler ON siparisler.yemek_id=yemekler.yemek_id
        GROUP BY masalar.masa_id, yemekler.isim, DATE(siparisler.eklenme_zamani)
        ORDER BY DATE(siparisler.eklenme_zamani) DESC
    """)
    return c.fetchall()

def garson_performans_raporu():
    c.execute("""
        SELECT isim, puan, aktif_masa, 0  -- '0'ı geç kalma sayısına göre güncelleyebilirsin
        FROM garsonlar
    """)
    return c.fetchall()

def garson_id_bul(masa_id):
    c.execute("SELECT garson_id FROM garsonlar WHERE aktif_masa=?", (masa_id,))
    result = c.fetchone()
    if result:
        return result[0]
    return None  