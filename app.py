from flask import Flask, render_template_string, request
import os
import psycopg2
from contextlib import contextmanager 

# Flask uygulamasının tanımlanması (Sözdizimi Hatası Düzeltildi: __name__)
app = Flask(__name__)

# Render'ın otomatik tanımladığı veritabanı bağlantı bilgisi (DATABASE_URL ortam değişkeni)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://clooud2_2_dp_user:lT7t7P1OWoTiIINtSuPoE3VrRF8IAGBr@dpg-d3ub82re5dus739hupo0-a.oregon-postgres.render.com/clooud2_2_dp")

# HTML ŞABLONU 
HTML ="""
<!doctype html>
<html>
<head>
<title>Buluttan Selam </title>
<style>
    body {font-family: Arial; text-align: center; padding: 50px; background: #eef2f3;}
    h1 { color: #333; }
    form{margin: 20px auto; }
    input { margin: 10px; font-size: 16px; }
    button { padding:10px 15px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer;}
    ul { list-style: none; padding: 0; }
    li {background: white; margin: 5px auto; width: 200px; padding: 8px; border-radius: 5px;}
  </style>
</head>
<body>
    <h1>Buluttan Selam</h1>
    <p>adını yaz, selamını bırak</p>
    <form method="POST">
        <input type="text" name="isim" placeholder="Adını yaz" required>
        <button type="submit">Gönder</button>
    </form>
    <h3>Ziyaretçiler</h3>
    <ul>
        {% for ad in isimler%}
            <li>{{ ad }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

# Güvenli bağlantı yönetimi için contextmanager kullanılır (Bağlantı yönetimi hatası düzeltildi)
@contextmanager
def connect_db():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    finally:
        # Bağlantının her zaman kapatılmasını garanti eder
        if conn:
            conn.close()

# Uygulama başlatıldığında bir kez çalışacak fonksiyon (Performans iyileştirildi)
def init_db():
    print("Veritabanı tablosu kontrol ediliyor...")
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                # Tablo sadece yoksa oluşturulur.
                cur.execute("CREATE TABLE IF NOT EXISTS ziyaretciler (id SERIAL PRIMARY KEY, isim TEXT NOT NULL)")
            conn.commit()
        print("Veritabanı tablosu hazır.")
    except Exception as e:
        print(f"HATA: Veritabanı başlatılırken sorun oluştu: {e}")
        # Hata durumunda uygulama devam etmeden önce sorunun çözülmesi gerekir

@app.route("/", methods=["GET", "POST"])
def index():
    isimler = []
    try:
        # Bağlantı ve Cursor (İmleç) with blokları ile güvenli yönetilir
        with connect_db() as conn:
            with conn.cursor() as cur:
                if request.method == "POST":
                    # İsim temizliği yapıldı
                    isim = (request.form.get("isim") or "").strip() 
                    
                    if isim:
                        # GÜVENLİ VERİ EKLEME (SQL Enjeksiyonu yok)
                        cur.execute("INSERT INTO ziyaretciler (isim) VALUES (%s)", (isim,))
                        conn.commit()

                # Verileri çekme
                cur.execute("SELECT isim FROM ziyaretciler ORDER BY id DESC LIMIT 10")
                isimler = [row[0] for row in cur.fetchall()]
                
        return render_template_string(HTML, isimler=isimler)


# Sözdizimi hataları düzeltildi: if __name__ == "__main__": ve app.run()
if __name__ == "__main__":
    init_db() # Önce veritabanı yapısını hazırla
    app.run(host="0.0.0.0", port=5000)
