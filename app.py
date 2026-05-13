from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
from routes.guru import guru_bp
from routes.topsis import topsis_bp
from routes.siswa import siswa_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
CORS(app)

# Registrasi Blueprint
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(guru_bp, url_prefix='/api')
app.register_blueprint(topsis_bp, url_prefix='/api')
app.register_blueprint(siswa_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({"message": "Backend SPK Guru Modular Aktif!"})

if __name__ == '__main__':
    import os

    # Mengambil port dari sistem (Railway), jika tidak ada baru pakai 5000
    port = int(os.environ.get("PORT", 5000))
    # Host harus 0.0.0.0 agar bisa diakses secara publik di server
    app.run(host='0.0.0.0', port=port)