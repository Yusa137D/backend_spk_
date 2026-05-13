from flask import Blueprint, jsonify
from database import get_db_connection

# Blueprint khusus untuk data Dashboard
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Menghitung jumlah Guru
        cursor.execute("SELECT COUNT(*) as total_guru FROM users WHERE role LIKE '%Guru%'")
        guru_count = cursor.fetchone()['total_guru']
        
        # Menghitung jumlah Siswa
        cursor.execute("SELECT COUNT(*) as total_siswa FROM users WHERE role LIKE '%Siswa%'")
        siswa_count = cursor.fetchone()['total_siswa']
        
        return jsonify({
            "total_guru": guru_count, 
            "total_siswa": siswa_count
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()