from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.routes.carbon_routes import carbon_bp
from app.routes.cost_routes import cost_bp
from app.routes.energy_routes import energy_bp


def create_app(config_class=Config):
    import os as _os

    _frontend = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../../frontend"))
    app = Flask(
        __name__, static_folder=_frontend if _os.path.isdir(_frontend) else None, static_url_path=""
    )
    app.config.from_object(config_class)
    # Support .env via python-dotenv if installed
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    app.config["MAX_CONTENT_LENGTH"] = app.config.get("MAX_CONTENT_LENGTH", 16 * 1024)

    # CORS configuration
    if app.config.get("CORS_ALLOW_ALL"):
        CORS(app)
    else:
        origins = app.config.get("CORS_ORIGINS", [])
        CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=False)

    # Rate limiter
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        Limiter(
            get_remote_address,
            app=app,
            default_limits=[f"{app.config.get('RATE_LIMIT_PER_MINUTE', 60)} per minute"],
            storage_uri="memory://",
        )
        # Exempt health
        app.config["RATELIMIT_ENABLED"] = not app.config.get("TESTING", False)
    except Exception as e:
        app.logger.warning(f"Limiter not enabled: {e}")

    # Security headers + manual CORS for dev (always allow for local dev)
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' https://fonts.googleapis.com "
            "https://cdnjs.cloudflare.com 'unsafe-inline'; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; connect-src 'self' https://cdn.jsdelivr.net"
        )
        # Always allow CORS for local dev (frontend on different port)
        from flask import request as flask_request

        origin = flask_request.headers.get("Origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response

    @app.before_request
    def handle_options():
        from flask import request as flask_request

        if flask_request.method == "OPTIONS":
            from flask import make_response

            resp = make_response("", 204)
            origin = flask_request.headers.get("Origin", "*")
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resp.headers["Access-Control-Max-Age"] = "3600"
            return resp

    # Register Blueprints
    app.register_blueprint(energy_bp, url_prefix="/api/energy")
    app.register_blueprint(cost_bp, url_prefix="/api/cost")
    app.register_blueprint(carbon_bp, url_prefix="/api/carbon")

    # Lazy imports to avoid circular deps
    try:
        from app.routes.solar_routes import solar_bp

        app.register_blueprint(solar_bp, url_prefix="/api/solar")
    except ImportError:
        pass
    try:
        from app.routes.history_routes import history_bp

        app.register_blueprint(history_bp, url_prefix="/api/history")
    except ImportError:
        pass
    try:
        from app.routes.advisor_routes import advisor_bp

        app.register_blueprint(advisor_bp, url_prefix="/api/advisor")
    except ImportError:
        pass

    # DB init if available
    try:
        from app.database import init_db

        init_db(app)
    except Exception:
        pass

    @app.route("/api/health")
    def health():
        return {"status": "success", "message": "ok"}

    @app.route("/")
    def index():
        import os as _os

        from flask import request as _req
        from flask import send_from_directory

        accept = _req.headers.get("Accept", "")
        # Serve frontend for browsers
        if "text/html" in accept and app.static_folder:
            idx = _os.path.join(app.static_folder, "index.html")
            if _os.path.exists(idx):
                return send_from_directory(app.static_folder, "index.html")
        # For direct browser open without Accept header, also try frontend
        # But keep JSON for API clients/tests (Accept: application/json or */*)
        if app.static_folder:
            idx = _os.path.join(app.static_folder, "index.html")
            if _os.path.exists(idx) and "text/html" in accept:
                return send_from_directory(app.static_folder, "index.html")
        return {"status": "success", "message": "EcoGrid AI API is running"}

    @app.route("/<path:path>")
    def serve_frontend(path):
        import os as _os

        from flask import jsonify, send_from_directory

        # Don't intercept API routes
        if path.startswith("api/"):
            return jsonify({"status": "error", "message": "Endpoint tidak ditemukan."}), 404
        if app.static_folder and _os.path.exists(_os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # Fallback to index.html for SPA
        idx = _os.path.join(app.static_folder or "", "index.html")
        if app.static_folder and _os.path.exists(idx):
            # Only serve index for non-api, non-static file paths that look like frontend
            if "." not in path or path.endswith(".html"):
                return send_from_directory(app.static_folder, "index.html")
        return jsonify({"status": "error", "message": "Endpoint tidak ditemukan."}), 404

    @app.errorhandler(400)
    def bad_request(e):
        # For malformed JSON, Flask raises BadRequest; ensure JSON response
        msg = getattr(e, "description", "Permintaan tidak valid.")
        # Malformed JSON typically has "Failed to decode" or proxy message
        if (
            "Failed to decode" in str(msg)
            or "could not understand" in str(msg)
            or "Bad Request" in str(e)
        ):
            msg = "JSON tidak valid. Periksa format payload."
        return jsonify({"status": "error", "message": msg}), 400

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"status": "error", "message": "Payload terlalu besar. Maksimum 16KB."}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Endpoint tidak ditemukan."}), 404

    @app.errorhandler(429)
    def too_many(e):
        return (
            jsonify({"status": "error", "message": "Terlalu banyak permintaan. Coba lagi nanti."}),
            429,
        )

    @app.errorhandler(500)
    def internal(e):
        return jsonify({"status": "error", "message": "Terjadi kesalahan internal."}), 500

    return app
