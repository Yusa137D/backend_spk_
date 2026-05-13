import warnings
import numpy as np
import pandas as pd
from database import get_db_connection

warnings.filterwarnings('ignore', category=UserWarning)

def hitung_topsis_logic():
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                g.id_guru, 
                g.nama_guru, 
                k.kode_kriteria, 
                AVG(j.skor_likert) as rata_skor
            FROM jawaban_kuesioner j
            JOIN guru g ON j.id_guru = g.id_guru
            JOIN pertanyaan p ON j.id_pertanyaan = p.id_pertanyaan
            JOIN kriteria k ON p.id_kriteria = k.id_kriteria
            GROUP BY g.id_guru, k.id_kriteria
        """
        df = pd.read_sql(query, conn)
        
        if df.empty or len(df['id_guru'].unique()) < 2:
            return []

        matrix = df.pivot(index='nama_guru', columns='kode_kriteria', values='rata_skor').fillna(0)
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT bobot, jenis FROM kriteria ORDER BY kode_kriteria")
        k_data = cursor.fetchall()
        weights = [float(k['bobot']) for k in k_data]
        types = [k['jenis'] for k in k_data]
        
        norm = matrix / np.sqrt((matrix**2).sum(axis=0))
        weighted = norm * weights
        
        a_p = []; a_m = []
        for i in range(len(types)):
            col = weighted.iloc[:, i]
            if types[i] == 'benefit':
                a_p.append(col.max()); a_m.append(col.min())
            else:
                a_p.append(col.min()); a_m.append(col.max())
        
        d_p = np.sqrt(((weighted - a_p)**2).sum(axis=1))
        d_m = np.sqrt(((weighted - a_m)**2).sum(axis=1))
        scores = d_m / (d_p + d_m)
        scores = scores.fillna(0) 
        
        results = []
        for i, nama in enumerate(matrix.index):
            id_g = int(df[df['nama_guru'] == nama]['id_guru'].iloc[0])
            nilai_ci = float(scores.iloc[i]) 
            predikat = "Sangat Baik" if nilai_ci >= 0.8 else "Baik" if nilai_ci >= 0.6 else "Cukup"
            
            results.append({
                "id_guru": id_g,
                "nama_guru": nama,
                "nilai_ci": nilai_ci,
                "predikat": predikat
            })
            
            cursor.execute("""
                INSERT INTO hasil_topsis (id_guru, nilai_topsis, predikat, id_periode) 
                VALUES (%s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE nilai_topsis = VALUES(nilai_topsis), predikat = VALUES(predikat)
            """, (id_g, nilai_ci, predikat))

        conn.commit()
        cursor.close()
        return sorted(results, key=lambda x: x['nilai_ci'], reverse=True)
    finally:
        # PENTING: Memastikan koneksi SELALU tertutup walau ada error saat kalkulasi pandas
        conn.close()