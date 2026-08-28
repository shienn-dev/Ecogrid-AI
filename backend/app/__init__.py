from flask import Flask
from flask_cors import CORS
from app.routes.energy_routes import energy_bp
from app.routes.cost_routes import cost_bp
from app.routes.carbon_routes import carbon_bp

def create_app():
    app = Flask(__name__)
    
    # Mengaktifkan CORS untuk seluruh rute agar dapat diakses dari frontend eksternal
    CORS(app)
    
    # Daftarkan Blueprint dengan prefix yang sesuai
    app.register_blueprint(energy_bp, url_prefix='/api/energy')
    app.register_blueprint(cost_bp, url_prefix='/api/cost')
    app.register_blueprint(carbon_bp, url_prefix='/api/carbon')
    
    @app.route('/')
    def index():
        return {
            "status": "success",
            "message": "EcoGrid AI API is running"
        }
        
    return app
