import random
import requests
import hashlib
from flask import Blueprint, request, jsonify
from database import get_db_connection
from config import Config # Import konfigurasi rahasia

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email_input = data.get('email')
    password_input = data.get('password')

    if not email_input or not email_input.endswith("@gmail.com"):
        return jsonify({"status": "error", "message": "Gunakan format email @gmail.com yang valid!"}), 400

    password_hashed = hash_password(password_input)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT id_user, username, email, no_wa, role FROM users WHERE email = %s AND password = %s AND status = 1"
        cursor.execute(query, (email_input, password_hashed))
        user = cursor.fetchone()
        
        if user:
            return jsonify({"status": "success", "message": "Login berhasil", "user": user}), 200
        else:
            return jsonify({"status": "error", "message": "Email atau Password salah!"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username_as_name = data.get('username') 
    email = data.get('email')
    no_wa = data.get('no_wa')
    password_raw = data.get('password')
    role = data.get('role')
    nomor_induk = data.get('nomor_induk') 
    kelas = data.get('kelas', "-")

    if not email or not email.endswith("@gmail.com"):
        return jsonify({"status": "error", "message": "Email harus @gmail.com"}), 400

    password_secure = hash_password(password_raw)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_user FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Email sudah terdaftar!"}), 400

        query_user = "INSERT INTO users (username, email, no_wa, password, role, status) VALUES (%s, %s, %s, %s, %s, 1)"
        cursor.execute(query_user, (username_as_name, email, no_wa, password_secure, role))
        user_id = cursor.lastrowid 

        if role == 'Guru':
            query_profil = "INSERT INTO guru (id_guru, nip, nama_guru, kelas, status_aktif) VALUES (%s, %s, %s, %s, 1)"
            cursor.execute(query_profil, (user_id, nomor_induk, username_as_name, kelas))
        elif role == 'Siswa':
            query_profil = "INSERT INTO siswa (id_siswa, nisn, nama_siswa, kelas) VALUES (%s, %s, %s, %s)"
            cursor.execute(query_profil, (user_id, nomor_induk, username_as_name, kelas))

        conn.commit()
        return jsonify({"status": "success", "message": "Registrasi berhasil! Silakan login."}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Gagal registrasi: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    if not email or not email.endswith("@gmail.com"):
        return jsonify({"message": "Gunakan format @gmail.com yang valid!"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id_user, username, no_wa FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "Email tidak terdaftar!"}), 404
        if not user['no_wa']:
            return jsonify({"message": "Nomor WhatsApp belum didaftarkan!"}), 400

        otp = str(random.randint(100000, 999999))
        cursor.execute("UPDATE users SET reset_otp = %s WHERE email = %s", (otp, email))
        conn.commit()

        target_wa = user['no_wa']
        pesan = f"Halo *{user['username']}*,\n\nKode OTP pemulihan password Anda adalah: *{otp}*\n\n_Jangan berikan kode ini kepada siapapun._"
        
        # Menggunakan Token dari Config
        headers = {'Authorization': Config.FONNTE_TOKEN}
        payload = {'target': target_wa, 'message': pesan, 'countryCode': '62'}
        requests.post("https://api.fonnte.com/send", headers=headers, data=payload)
        
        return jsonify({"status": "success", "message": f"OTP terkirim ke WhatsApp ({target_wa})"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password_raw = data.get('new_password')
    new_password_secure = hash_password(new_password_raw)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_user FROM users WHERE email = %s AND reset_otp = %s", (email, otp))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Kode OTP salah!"}), 400

        cursor.execute("UPDATE users SET password = %s, reset_otp = NULL WHERE email = %s", (new_password_secure, email))
        conn.commit()
        return jsonify({"status": "success", "message": "Password berhasil diubah!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()