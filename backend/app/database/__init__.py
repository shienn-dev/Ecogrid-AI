from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    # Config
    import os

    db_url = app.config.get("DATABASE_URL") or "sqlite:///database/energy.db"
    # Convert relative sqlite path to absolute to avoid instance folder confusion
    if db_url.startswith("sqlite") and "///" in db_url and ":memory:" not in db_url:
        try:
            # Extract path part after ///
            path = db_url.split("///")[-1].split("?")[0]
            if path and not os.path.isabs(path):
                backend_dir = os.path.abspath(os.path.join(app.root_path, os.pardir))
                full = os.path.join(backend_dir, path)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                # Use absolute URI (forward slashes for Windows)
                full_forward = full.replace("\\", "/")
                # Ensure 3 slashes for absolute: sqlite:///D:/...
                db_url = f"sqlite:///{full_forward}"
        except Exception:
            pass
    # Flask-SQLAlchemy expects SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(app)
    # Create tables
    with app.app_context():
        try:
            # import models to register
            import app.models.simulation  # noqa: F401

            db.create_all()
        except Exception as e:
            app.logger.warning(f"DB init warning: {e}")
