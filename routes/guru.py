from flask import Blueprint, request, jsonify
from database import get_db_connection

guru_bp = Blueprint('guru', __name__)

@guru_bp.route('/guru', methods=['GET'])
def get_guru():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM guru WHERE status_aktif = 1")
        res = cursor.fetchall()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@guru_bp.route('/guru', methods=['POST'])
def add_guru():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO guru (nip, nama_guru, mata_pelajaran, kelas, status_aktif) VALUES (%s, %s, %s, %s, 1)"
        cursor.execute(query, (data['nip'], data['nama_guru'], data.get('mata_pelajaran', '-'), data['kelas']))
        conn.commit()
        return jsonify({"message": "Berhasil ditambahkan"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@guru_bp.route('/guru/update/<int:id_guru>', methods=['PUT'])
def update_guru(id_guru):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE guru SET nama_guru=%s, nip=%s, kelas=%s WHERE id_guru=%s", 
                       (data['nama_guru'], data['nip'], data['kelas'], id_guru))
        cursor.execute("UPDATE users SET username=%s WHERE id_user=%s", (data['nama_guru'], id_guru))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@guru_bp.route('/guru/delete/<int:id_guru>', methods=['DELETE'])
def delete_guru(id_guru):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id_user = %s", (id_guru,))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()