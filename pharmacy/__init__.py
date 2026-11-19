import logging
import os
from decimal import Decimal

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import BASE_DIR, ON_VERCEL, load_config
from .extensions import csrf, db

CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "font-src 'self' https://cdn.jsdelivr.net",
    "img-src 'self' data:",
    "connect-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
])


def inr(value):
    """Format a number as Indian rupees with lakh grouping: 123456.5 -> 1,23,456.50"""
    if value is None:
        return ""
    value = Decimal(value).quantize(Decimal("0.01"))
    sign = "-" if value < 0 else ""
    whole, frac = f"{abs(value):.2f}".split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    return f"{sign}{whole}.{frac}"


def create_app(overrides=None):
    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, "public", "static"),
        static_url_path="/static",
    )
    app.config.update(load_config())
    if overrides:
        app.config.update(overrides)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    db.init_app(app)
    csrf.init_app(app)

    from . import audit  # noqa: F401  (registers the flush listener)
    from .auth import bp as auth_bp
    from .views.inventory import bp as inventory_bp
    from .views.portal import bp as portal_bp
    from .views.public import bp as public_bp
    from .views.reports import bp as reports_bp
    from .views.sales import bp as sales_bp
    from .views.staff import bp as staff_bp

    for bp in (public_bp, auth_bp, staff_bp, inventory_bp, sales_bp, reports_bp, portal_bp):
        app.register_blueprint(bp)

    from .models import SCHEDULES, to_local

    app.jinja_env.globals["SCHEDULES"] = SCHEDULES

    app.jinja_env.filters["inr"] = inr
    app.jinja_env.filters["local"] = lambda dt, fmt="%d %b %Y %H:%M": to_local(dt).strftime(fmt) if dt else ""

    @app.context_processor
    def globals_for_templates():
        from .models import PharmacySettings

        from .models import local_today

        return {"today": local_today(),
                "pharmacy": PharmacySettings.get()}

    @app.after_request
    def security_headers(response):
        h = response.headers
        h.setdefault("Content-Security-Policy", CSP)
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "same-origin")
        h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        if request.is_secure or ON_VERCEL:
            h.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        if not request.path.startswith("/static/"):
            # Pages carry patient and billing data; keep them out of every cache.
            h["Cache-Control"] = "no-store"
        return response

    def error_page(code, title, message):
        return render_template("error.html", code=code, title=title, message=message), code

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return error_page(400, "Form expired", "Your session may have timed out. Go back, reload "
                          "the page and try again.")

    @app.errorhandler(403)
    def forbidden(error):
        return error_page(403, "Not allowed", "Your account cannot open this page.")

    @app.errorhandler(404)
    def not_found(error):
        return error_page(404, "Page not found", "The page you asked for does not exist.")

    @app.errorhandler(413)
    def too_large(error):
        return error_page(413, "Too large", "That upload or form is too large.")

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return error_page(500, "Something went wrong", "The error has been logged. Try again in "
                          "a moment.")

    with app.app_context():
        from . import models

        db.create_all()
        models.PharmacySettings.get()
        db.session.commit()
        if app.config["SEED_DEMO_DATA"] and models.Employee.query.first() is None:
            from .seed import populate

            app.logger.info("Empty database, loading demo data")
            populate()

    return app
