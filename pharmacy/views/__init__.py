"""Small helpers shared by the view modules."""
import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Response, request


class FormError(ValueError):
    pass


def text(name, label=None, required=True, max_len=200, default=""):
    value = request.form.get(name, default).strip()
    if required and not value:
        raise FormError(f"{label or name.replace('_', ' ').capitalize()} is required.")
    if len(value) > max_len:
        raise FormError(f"{label or name} is too long (max {max_len} characters).")
    return value


def integer(name, label=None, required=True, minimum=None, maximum=None):
    raw = request.form.get(name, "").strip()
    if not raw:
        if required:
            raise FormError(f"{label or name} is required.")
        return None
    try:
        value = int(raw)
    except ValueError:
        raise FormError(f"{label or name} must be a whole number.") from None
    if minimum is not None and value < minimum:
        raise FormError(f"{label or name} must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise FormError(f"{label or name} must be at most {maximum}.")
    return value


def money(name, label=None, required=True, minimum=Decimal("0")):
    raw = request.form.get(name, "").strip().replace(",", "")
    if not raw:
        if required:
            raise FormError(f"{label or name} is required.")
        return None
    try:
        value = Decimal(raw).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise FormError(f"{label or name} must be a number.") from None
    if value < minimum:
        raise FormError(f"{label or name} cannot be negative.")
    return value


def a_date(name, label=None, required=True):
    raw = request.form.get(name, "").strip()
    if not raw:
        if required:
            raise FormError(f"{label or name} is required.")
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        raise FormError(f"{label or name} must be a date.") from None


def arg_date(name, default):
    try:
        return datetime.strptime(request.args.get(name, ""), "%Y-%m-%d").date()
    except ValueError:
        return default


def month_bounds(day):
    start = day.replace(day=1)
    end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    return start, end


def csv_response(filename, header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    for row in rows:
        # Stop spreadsheet formula injection from user-entered text.
        writer.writerow([f"'{v}" if isinstance(v, str) and v[:1] in "=+-@" else v for v in row])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
