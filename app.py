# app.py
from flask import Flask, request, jsonify
import mariadb

app = Flask(__name__)

DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "cafe_db",
}

def conn():
    return mariadb.connect(**DB)

@app.get("/products")
def get_products():
    try:
        c = conn(); cur = c.cursor()
        cur.execute("SELECT id, name, CAST(is_available AS UNSIGNED), rate FROM product ORDER BY id")
        rows = cur.fetchall()
        cur.close(); c.close()
        return jsonify([
            {"id": r[0], "name": r[1], "is_available": bool(r[2]), "rating": r[3]}
            for r in rows
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/product/<int:pid>")
def get_product(pid):
    try:
        c = conn(); cur = c.cursor()
        cur.execute("SELECT id, name, CAST(is_available AS UNSIGNED), rate FROM product WHERE id = ?", (pid,))
        r = cur.fetchone()
        cur.close(); c.close()
        if not r:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": r[0], "name": r[1], "is_available": bool(r[2]), "rating": r[3]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/add")
def add_product():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    name = data["name"].strip()
    is_available = 1 if data.get("is_available", True) else 0
    rating = int(data.get("rating", 0))

    try:
        c = conn(); cur = c.cursor()
        if "id" in data:  # tablo AUTO_INCREMENT değilse id gönder
            pid = int(data["id"])
            cur.execute("INSERT INTO product (id, name, is_available, rate) VALUES (?, ?, ?, ?)",
                        (pid, name, is_available, rating))
            new_id = pid
        else:             # AUTO_INCREMENT varsa id göndermeyebilirsin
            cur.execute("INSERT INTO product (name, is_available, rate) VALUES (?, ?, ?)",
                        (name, is_available, rating))
            new_id = cur.lastrowid
        c.commit()
        cur.close(); c.close()
        return jsonify({"id": new_id, "name": name, "is_available": bool(is_available), "rating": rating}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE: Delete a product by ID
@app.delete("/delete_product/<int:pid>")
def delete_product(pid):
    try:
        c = conn(); cur = c.cursor()
        cur.execute("DELETE FROM product WHERE id = ?", (pid,))
        affected = cur.rowcount
        c.commit()
        cur.close(); c.close()
        if affected == 0:
            return jsonify({"error": "not found"}), 404
        return jsonify({"message": f"Product {pid} deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PUT: Update an existing product
@app.put("/update_product")
def update_product():
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "id is required"}), 400

    pid = int(data["id"])
    name = data.get("name", "").strip()
    is_available = 1 if data.get("is_available", True) else 0
    rating = int(data.get("rating", 0))

    try:
        c = conn(); cur = c.cursor()
        cur.execute(
            "UPDATE product SET name = ?, is_available = ?, rate = ? WHERE id = ?",
            (name, is_available, rating, pid)
        )
        affected = cur.rowcount
        c.commit()
        cur.close(); c.close()
        if affected == 0:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": pid, "name": name, "is_available": bool(is_available), "rating": rating}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)