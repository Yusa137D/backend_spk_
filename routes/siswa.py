from flask import Blueprint, request, jsonify
from database import get_db_connection

siswa_bp = Blueprint('siswa', __name__)

@siswa_bp.route('/daftar-siswa', methods=['GET'])
def get_daftar_siswa():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                u.id_user, 
                u.email, 
                COALESCE(s.nisn, '-') AS nisn, 
                COALESCE(s.nama_siswa, u.username) AS nama_siswa, 
                COALESCE(s.kelas, '-') AS kelas 
            FROM users u
            LEFT JOIN siswa s ON u.id_user = s.id_siswa
            WHERE LOWER(u.role) = 'siswa'
            ORDER BY nama_siswa ASC
        """
        cursor.execute(query)
        siswa_list = cursor.fetchall()
        return jsonify(siswa_list), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@siswa_bp.route('/hapus-siswa/<int:id_user>', methods=['DELETE'])
def hapus_siswa(id_user):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM jawaban_kuesioner WHERE id_user_responden = %s", (id_user,))
        cursor.execute("DELETE FROM siswa WHERE id_siswa = %s", (id_user,))
        cursor.execute("DELETE FROM users WHERE id_user = %s", (id_user,))
        conn.commit()
        return jsonify({"status": "success", "message": "Data siswa berhasil dihapus!"}), 200
    except Exception as e:
        conn.rollback() 
        return jsonify({"status": "error", "message": f"Gagal menghapus: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@siswa_bp.route('/update-siswa/<int:id_user>', methods=['PUT'])
def update_siswa(id_user):
    data = request.json
    nama = data.get('nama_siswa')
    nisn = data.get('nisn')
    kelas = data.get('kelas')
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query_siswa = "UPDATE siswa SET nama_siswa = %s, nisn = %s, kelas = %s WHERE id_siswa = %s"
        cursor.execute(query_siswa, (nama, nisn, kelas, id_user))
        query_users = "UPDATE users SET email = %s, username = %s WHERE id_user = %s"
        cursor.execute(query_users, (email, nama, id_user))
        
        conn.commit()
        return jsonify({"status": "success", "message": "Data siswa diperbarui!"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()