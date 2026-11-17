import logging
import os
import secrets
from datetime import date

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db
from routes import admin_routes, auth_routes, customer_routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ON_VERCEL = bool(os.environ.get("VERCEL"))

csrf = CSRFProtect()


def _database_url():
    url = os.environ.get("DATABASE_URL")
    if url:
        # Heroku/Neon style URLs use the old "postgres://" scheme.
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url
    if ON_VERCEL:
        # The deployment filesystem is read-only; /tmp is writable but is
        # reset between cold starts. Set DATABASE_URL for persistent data.
        return "sqlite:////tmp/pharmacy.db"
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    return "sqlite:///" + os.path.join(BASE_DIR, "instance", "pharmacy.db")


def _secret_key():
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    if ON_VERCEL:
        raise RuntimeError("SECRET_KEY must be set in the Vercel project settings.")
    return secrets.token_hex(32)


def _seed_enabled(db_url):
    flag = os.environ.get("SEED_DEMO_DATA")
    if flag is not None:
        return flag.lower() in ("1", "true", "yes")
    return db_url.startswith("sqlite")


def create_app():
    app = Flask(
        __name__,
        static_folder="public/static",
        static_url_path="/static",
    )

    db_url = _database_url()
    app.config.update(
        SECRET_KEY=_secret_key(),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=ON_VERCEL,
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(customer_routes)

    with app.app_context():
        import models  # noqa: F401  (registers tables)

        db.create_all()
        if _seed_enabled(db_url) and models.Employee.query.first() is None:
            from seed_data import populate

            app.logger.info("Empty database, loading demo data")
            populate()

    @app.context_processor
    def inject_globals():
        return {"date": date}

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template("400.html", reason=error.description), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5000)))
