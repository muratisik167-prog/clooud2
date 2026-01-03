from flask import Flask, render_template_string, request
import os
import psycopg2
from contextlib import contextmanager

# Flask uygulamasının tanımlanması
app = Flask(__name__)

# Render'ın otomatik tanımladığı veritabanı bağlantı bilgisi
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cloud2_user:KbeZWD5LqQjpXnTw6RDvz8YcuBzkaOWS@dpg-d5chscf5r7bs73b1qll0-a.oregon-postgres.render.com/cloud2")

# HTML ŞABLONU 
HTML ="""
<!doctype html>
<html>
<head>
<title>murat işık</title>
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
    <h1>buluttan selam</h1>
    <p>adını yaz, selamını bırak</p>

    <form method="POST">
        <input type="text" name="isim" placeholder="Adını yaz" required>
        <button type="submit">Gönder</button>
    </form>
    <h3>Ziyaretçiler</h3>
    <ul>
        {% for ad_tuple in isimler %}
            <li>{{ ad_tuple[0] }}</li> 
        {% endfor %}
    </ul>
</body>
</html>
"""

# Güvenli bağlantı yönetimi için contextmanager
@contextmanager
def connect_db():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    finally:
        if conn:
            conn.close()

# Uygulama başlatıldığında bir kez çalışacak fonksiyon
def init_db():
    print("Veritabanı tablosu kontrol ediliyor...")
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS ziyaretciler (id SERIAL PRIMARY KEY, isim TEXT NOT NULL)")
            conn.commit()
        print("Veritabanı tablosu hazır.")
    except Exception as e:
        print(f"HATA: Veritabanı başlatılırken sorun oluştu: {e}") 

@app.route("/", methods=["GET", "POST"])
def index():
    isimler = []
    try:
        # Bağlantı ve Cursor güvenli yönetilir
        with connect_db() as conn:
            with conn.cursor() as cur:
                if request.method == "POST":
                    isim = (request.form.get("isim") or "").strip() 
                    
                    if isim:
                        # GÜVENLİ VERİ EKLEME
                        cur.execute("INSERT INTO ziyaretciler (isim) VALUES (%s)", (isim,))
                        conn.commit()

                # ÖNEMLİ DÜZELTME: Veritabanından verileri çekme işlemi hem POST hem GET için çalışır
                cur.execute("SELECT isim FROM ziyaretciler ORDER BY id DESC")
                isimler = cur.fetchall() # Sonuçlar çekilir

    except Exception as e:
        print(f"HATA: Veritabanı işlemi sırasında hata: {e}")
        # Hata oluşsa bile sayfa boş liste ile gösterilir

    # Sayfa artık isimler listesi ile render edilir
    return render_template_string(HTML, isimler=isimler)


if __name__ == "__main__":
    init_db() # Önce veritabanı yapısını hazırla
    # Host ve Port Render ortamına uygun olarak ayarlanır
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
