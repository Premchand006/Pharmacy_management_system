"""Sign-in, sessions and access control for staff and customers."""
from datetime import timedelta
from functools import wraps

from flask import (Blueprint, abort, flash, g, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from . import audit
from .extensions import db
from .models import Customer, Employee, LoginAttempt, utcnow

bp = Blueprint("auth", __name__)

# scrypt with N=2^17, r=8, p=1: the OWASP minimum for scrypt. Werkzeug's
# default is N=2^15, so older hashes are upgraded at the next sign-in.
HASH_METHOD = "scrypt:131072:8:1"
MIN_PASSWORD = 12
LOCK_WINDOW = timedelta(minutes=15)
MAX_FAILS_PER_ACCOUNT = 5
MAX_FAILS_PER_IP = 20
COMMON = {"password1234", "123456789012", "qwertyuiopas", "pharmacy1234", "admin1234567",
          "iloveyou1234", "password@123", "welcome12345"}


def hash_password(password):
    return generate_password_hash(password, method=HASH_METHOD)


def password_problem(password):
    """Return a message if a new password is not acceptable, else None."""
    if len(password) < MIN_PASSWORD:
        return f"Use at least {MIN_PASSWORD} characters."
    if len(password) > 128:
        return "Use at most 128 characters."
    if password.lower() in COMMON or len(set(password)) < 4:
        return "That password is too easy to guess."
    return None


def _client_ip():
    return request.remote_addr or ""


def _locked(portal, identifier):
    since = utcnow() - LOCK_WINDOW
    q = LoginAttempt.query.filter(LoginAttempt.portal == portal, LoginAttempt.success.is_(False),
                                  LoginAttempt.at >= since)
    if q.filter(LoginAttempt.identifier == identifier).count() >= MAX_FAILS_PER_ACCOUNT:
        return True
    return q.filter(LoginAttempt.ip == _client_ip()).count() >= MAX_FAILS_PER_IP


def _note_attempt(portal, identifier, success):
    db.session.add(LoginAttempt(portal=portal, identifier=identifier, ip=_client_ip(),
                                success=success))
    db.session.commit()


def _check(user, password):
    if not user or not user.is_active or not user.password_hash or not password:
        # Spend similar time either way so the response does not reveal
        # whether the account exists.
        check_password_hash(_DUMMY_HASH, password or "x")
        return False
    if not check_password_hash(user.password_hash, password):
        return False
    if not user.password_hash.startswith(HASH_METHOD):
        user.password_hash = hash_password(password)
    return True


_DUMMY_HASH = generate_password_hash("not-a-real-password", method=HASH_METHOD)


def _start_session(kind, user):
    session.clear()
    session.permanent = True
    session["kind"] = kind
    session["uid"] = user.e_id if kind == "staff" else user.c_id
    session["ver"] = user.session_version


@bp.before_app_request
def load_user():
    g.user = None
    g.user_kind = None
    kind, uid = session.get("kind"), session.get("uid")
    if not kind or uid is None:
        return
    model = Employee if kind == "staff" else Customer
    user = db.session.get(model, uid)
    if user is None or not user.is_active or user.session_version != session.get("ver"):
        session.clear()
        return
    g.user, g.user_kind = user, kind


def staff_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user_kind != "staff":
            return redirect(url_for("auth.staff_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user_kind != "staff":
            return redirect(url_for("auth.staff_login", next=request.path))
        if not g.user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def customer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user_kind != "customer":
            return redirect(url_for("auth.customer_login"))
        return view(*args, **kwargs)
    return wrapped


def _safe_next(default):
    target = request.args.get("next", "")
    if target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return default


@bp.route("/login", methods=["GET", "POST"])
def staff_login():
    if g.user_kind == "staff":
        return redirect(url_for("staff.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        if _locked("staff", username):
            flash("Too many failed attempts. Wait 15 minutes and try again.", "error")
            return render_template("auth/staff_login.html", username=username), 429
        user = Employee.query.filter(db.func.lower(Employee.username) == username).first() if username else None
        if _check(user, password):
            _note_attempt("staff", username, True)
            _start_session("staff", user)
            g.user, g.user_kind = user, "staff"
            audit.record(db.session, "login", "Employee", user.e_id)
            db.session.commit()
            return redirect(_safe_next(url_for("staff.dashboard")))
        _note_attempt("staff", username, False)
        flash("Username or password is incorrect.", "error")
        return render_template("auth/staff_login.html", username=username), 401
    return render_template("auth/staff_login.html", username="")


@bp.route("/portal/login", methods=["GET", "POST"])
def customer_login():
    if g.user_kind == "customer":
        return redirect(url_for("portal.home"))
    if request.method == "POST":
        ident = request.form.get("customer_id", "").strip()
        password = request.form.get("password", "")
        if _locked("customer", ident):
            flash("Too many failed attempts. Wait 15 minutes and try again.", "error")
            return render_template("auth/customer_login.html", customer_id=ident), 429
        user = db.session.get(Customer, int(ident)) if ident.isdigit() else None
        if _check(user, password):
            _note_attempt("customer", ident, True)
            _start_session("customer", user)
            db.session.commit()
            return redirect(url_for("portal.home"))
        _note_attempt("customer", ident, False)
        flash("Customer ID or password is incorrect.", "error")
        return render_template("auth/customer_login.html", customer_id=ident), 401
    return render_template("auth/customer_login.html", customer_id="")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("public.index"))


@bp.route("/account/password", methods=["GET", "POST"])
def change_password():
    if g.user is None:
        return redirect(url_for("public.index"))
    if request.method == "POST":
        current = request.form.get("current", "")
        new = request.form.get("new", "")
        if not check_password_hash(g.user.password_hash or _DUMMY_HASH, current):
            flash("Your current password is wrong.", "error")
        elif new != request.form.get("confirm", ""):
            flash("The new passwords do not match.", "error")
        elif (problem := password_problem(new)):
            flash(problem, "error")
        else:
            g.user.password_hash = hash_password(new)
            # Signs out every other device using the old session.
            g.user.session_version += 1
            db.session.commit()
            session["ver"] = g.user.session_version
            flash("Password changed. Other devices have been signed out.", "success")
            return redirect(url_for("staff.dashboard" if g.user_kind == "staff" else "portal.home"))
    return render_template("auth/change_password.html", min_length=MIN_PASSWORD)
