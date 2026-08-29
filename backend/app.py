import os
import sys

# Memastikan direktori backend terdaftar di sys.path agar import modul 'app' berjalan lancar
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.config import Config

app = create_app(Config)

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes") or Config.DEBUG
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug, host=host, port=port)