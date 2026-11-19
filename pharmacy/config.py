import os
import secrets
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ON_VERCEL = bool(os.environ.get("VERCEL"))


def _database_url():
    url = os.environ.get("DATABASE_URL")
    if url:
        # Neon/Heroku style URLs use the old "postgres://" scheme.
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url
    if ON_VERCEL:
        # Read-only filesystem except /tmp, which is wiped between cold
        # starts. Fine for a preview, never for real data.
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


def _flag(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def load_config():
    db_url = _database_url()
    fallbacks = [k for k in os.environ.get("SECRET_KEY_FALLBACKS", "").split(",") if k.strip()]
    trusted = [h for h in os.environ.get("TRUSTED_HOSTS", "").split(",") if h.strip()]
    engine_options = {"pool_pre_ping": True}
    if db_url.startswith("postgresql"):
        engine_options.update(pool_size=2, max_overflow=2, pool_recycle=300)

    return {
        "SECRET_KEY": _secret_key(),
        "SECRET_KEY_FALLBACKS": fallbacks,
        "TRUSTED_HOSTS": trusted or None,
        "SQLALCHEMY_DATABASE_URI": db_url,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": engine_options,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": ON_VERCEL,
        "PERMANENT_SESSION_LIFETIME": timedelta(minutes=int(os.environ.get("SESSION_MINUTES", "60"))),
        "MAX_CONTENT_LENGTH": 1024 * 1024,
        "WTF_CSRF_TIME_LIMIT": None,  # token lives as long as the session
        "SEED_DEMO_DATA": _flag("SEED_DEMO_DATA", db_url.startswith("sqlite")),
        "PREFERRED_URL_SCHEME": "https" if ON_VERCEL else "http",
    }
