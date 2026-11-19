from flask import Blueprint, g, redirect, render_template, url_for

from ..extensions import db

bp = Blueprint("public", __name__)


@bp.route("/")
def index():
    if g.user_kind == "staff":
        return redirect(url_for("staff.dashboard"))
    if g.user_kind == "customer":
        return redirect(url_for("portal.home"))
    return render_template("public/index.html")


@bp.route("/privacy")
def privacy():
    return render_template("public/privacy.html")


@bp.route("/healthz")
def healthz():
    db.session.execute(db.text("SELECT 1"))
    return {"status": "ok"}


@bp.route("/robots.txt")
def robots():
    body = "User-agent: *\nAllow: /$\nAllow: /privacy\nDisallow: /\n"
    return body, 200, {"Content-Type": "text/plain"}
