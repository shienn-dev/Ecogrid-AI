from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    # Config
    db_url = app.config.get("DATABASE_URL") or "sqlite:///database/energy.db"
    # Flask-SQLAlchemy expects SQLALCHEMY_DATABASE_URI
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", db_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    # Ensure path exists for sqlite
    if db_url.startswith("sqlite") and "///" in db_url:
        import os

        # extract file path
        try:
            path = db_url.split("///")[-1].split("?")[0]
            # relative to backend/ root? Flask-SQLAlchemy resolves relative to instance
            # ensure directory exists: backend/database/
            if path and not path.startswith(":memory:"):
                # path is like database/energy.db (relative to backend)
                # app.root_path is backend/app, so dirname is backend
                backend_dir = os.path.abspath(os.path.join(app.root_path, os.pardir))
                full = os.path.join(backend_dir, path) if not os.path.isabs(path) else path
                os.makedirs(os.path.dirname(full), exist_ok=True)
        except Exception:
            pass
    db.init_app(app)
    # Create tables
    with app.app_context():
        try:
            # import models to register
            import app.models.simulation  # noqa: F401

            db.create_all()
        except Exception as e:
            app.logger.warning(f"DB init warning: {e}")
