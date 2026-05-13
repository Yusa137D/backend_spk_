from flask import Blueprint, jsonify, request, send_file
from logic import hitung_topsis_logic
from database import get_db_connection
from fpdf import FPDF
import io

topsis_bp = Blueprint('topsis', __name__)

# --- AMBIL DAFTAR GURU BESERTA STATUS PENILAIAN ---
@topsis_bp.route('/daftar-guru/<int:id_user>', methods=['GET'])
def get_daftar_guru(id_user):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Pengecekan otomatis (Real-time) apakah id_user sudah menilai guru ini
        query = """
            SELECT 
                g.id_guru, 
                g.nama_guru, 
                g.nip, 
                g.mata_pelajaran,
                g.kelas,
                IF(
                    (SELECT COUNT(*) 
                     FROM jawaban_kuesioner jk 
                     WHERE jk.id_guru = g.id_guru 
                     AND jk.id_user_responden = %s) > 0, 
                    1, 0
                ) AS sudah_dinilai
            FROM guru g 
            WHERE g.status_aktif = 1
        """
        cursor.execute(query, (id_user,))
        data = cursor.fetchall()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- DASHBOARD GURU: LIHAT NILAI SENDIRI ---
@topsis_bp.route('/nilai-saya/<int:id_guru>', methods=['GET'])
def get_nilai_saya(id_guru):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT nilai_topsis, predikat FROM hasil_topsis WHERE id_guru = %s"
        cursor.execute(query, (id_guru,))
        data = cursor.fetchone()
        if data:
            return jsonify(data), 200
        return jsonify({"message": "Belum ada penilaian"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- AMBIL DAFTAR PERTANYAAN ---
@topsis_bp.route('/pertanyaan', methods=['GET'])
def get_pertanyaan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_pertanyaan as id, pertanyaan as teks FROM pertanyaan")
        data = cursor.fetchall()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- SIMPAN JAWABAN KUESIONER ---
@topsis_bp.route('/simpan-jawaban', methods=['POST'])
def simpan_jawaban():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for item in data:
            query = "INSERT INTO jawaban_kuesioner (id_user_responden, id_guru, id_pertanyaan, skor_likert, id_periode) VALUES (%s, %s, %s, %s, 1)"
            cursor.execute(query, (item['id_user'], item['id_guru'], item['id_pertanyaan'], item['skor']))
        conn.commit()
        # Hitung ulang TOPSIS agar tabel hasil_topsis terupdate otomatis
        hitung_topsis_logic()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --- RANKING TOPSIS ---
@topsis_bp.route('/hitung-topsis', methods=['GET'])
def get_ranking():
    results = hitung_topsis_logic()
    return jsonify(results)

# --- CETAK PDF ---
@topsis_bp.route('/print-pdf', methods=['GET'])
def print_pdf():
    results = hitung_topsis_logic()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "LAPORAN PENILAIAN GURU (TOPSIS)", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(10, 10, "No", 1); pdf.cell(80, 10, "Nama Guru", 1)
    pdf.cell(50, 10, "Nilai Ci", 1); pdf.cell(50, 10, "Predikat", 1); pdf.ln()
    
    pdf.set_font("Arial", '', 12)
    for i, r in enumerate(results):
        pdf.cell(10, 10, str(i+1), 1)
        pdf.cell(80, 10, r['nama_guru'], 1)
        pdf.cell(50, 10, str(round(r['nilai_ci'], 4)), 1)
        pdf.cell(50, 10, r['predikat'], 1); pdf.ln()
    
    output = io.BytesIO()
    pdf_str = pdf.output(dest='S').encode('latin-1')
    output.write(pdf_str)
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name="Ranking_Guru.pdf")