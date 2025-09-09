# app.py
from flask import Flask, jsonify
import mariadb

app = Flask(__name__)

# MariaDB bağlantı bilgileri
DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",              # kendi kullanıcın
    "password": "1234",  # kendi şifren
    "database": "cafe_db",
}

def row_to_product(row):
    pid, name, available, rate = row
    # is_available sütunu BIT(1) ise b'\x01' şeklinde gelebilir → bool'a çevir
    if isinstance(available, (bytes, bytearray, memoryview)):
        available = int.from_bytes(available, "little")
    return {
        "id": int(pid),
        "name": name,
        "is_available": (bool(available) if available is not None else None),
        "rate": (int(rate) if rate is not None else None),
    }

@app.get("/products")  # 1) Tüm ürünleri döndür
def get_products():
    try:
        conn = mariadb.connect(**DB)
        cur = conn.cursor()
        cur.execute("SELECT id, name, is_available, rate FROM product ORDER BY id")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([row_to_product(r) for r in rows]), 200
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500

@app.get("/product/<int:pid>")  # 2) Tek ürün (id ile)
def get_product(pid: int):
    try:
        conn = mariadb.connect(**DB)
        cur = conn.cursor()
        cur.execute("SELECT id, name, is_available, rate FROM product WHERE id = ?", (pid,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(row_to_product(row)), 200
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
