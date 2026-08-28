import os
import sys

# Memastikan direktori backend terdaftar di sys.path agar import modul 'app' berjalan lancar
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Menjalankan Flask di port 5000 dengan mode debug aktif
    app.run(debug=True, host="127.0.0.1", port=5000)