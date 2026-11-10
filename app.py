"""FitFinder: a community web app where shoppers post how clothing fits them
and browse reviews from people with a similar body type.

Run with:  python app.py   then open http://127.0.0.1:5000
"""
import json
import os
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = BASE_DIR / "data" / "reviews.json"

BUILDS = ["Petite", "Slim", "Average", "Athletic", "Curvy", "Plus Size"]
BUILD_GUIDE = [
    ("Petite", "short with a small frame"),
    ("Slim", "narrow, lean frame"),
    ("Average", "medium frame"),
    ("Athletic", "broad shoulders, muscular"),
    ("Curvy", "fuller hips and bust"),
    ("Plus Size", "fuller figure throughout"),
]
FIT_RATINGS = ["Runs small", "True to size", "Runs large"]
MIN_HEIGHT_CM = 100
MAX_HEIGHT_CM = 250

app = Flask(__name__)
app.config["DATA_FILE"] = os.environ.get("FITFINDER_DATA", str(DEFAULT_DATA_FILE))
_lock = threading.Lock()


# ---------------------------------------------------------------- storage
def data_path():
    return Path(app.config["DATA_FILE"])


def load_reviews():
    """Return all saved reviews, oldest first. A missing file means no reviews."""
    path = data_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_reviews(reviews):
    """Write reviews to disk atomically so a crash never leaves a half-written file."""
    path = data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def add_review(review):
    with _lock:
        reviews = load_reviews()
        review = dict(review)
        review["id"] = uuid.uuid4().hex
        review["created"] = datetime.now(timezone.utc).isoformat()
        reviews.append(review)
        save_reviews(reviews)


# ---------------------------------------------------------------- validation
def validate_review(form):
    """Check a submitted review. Returns (clean_review, errors)."""
    errors = {}
    brand = form.get("brand", "").strip()
    item = form.get("item", "").strip()
    size = form.get("size", "").strip()
    height_raw = form.get("height", "").strip()
    build = form.get("build", "").strip()
    fit = form.get("fit", "").strip()

    if not brand:
        errors["brand"] = "Brand is required"
    elif len(brand) > 50:
        errors["brand"] = "Brand must be 50 characters or fewer"
    if not item:
        errors["item"] = "Item is required"
    elif len(item) > 80:
        errors["item"] = "Item must be 80 characters or fewer"
    if not size:
        errors["size"] = "Size worn is required"
    elif len(size) > 20:
        errors["size"] = "Size must be 20 characters or fewer"

    height = None
    if height_raw.isdigit() and MIN_HEIGHT_CM <= int(height_raw) <= MAX_HEIGHT_CM:
        height = int(height_raw)
    else:
        errors["height"] = f"Enter a height between {MIN_HEIGHT_CM} and {MAX_HEIGHT_CM} cm"

    if build not in BUILDS:
        errors["build"] = "Choose your build"
    if fit not in FIT_RATINGS:
        errors["fit"] = "Choose a fit rating"

    clean = {"brand": brand, "item": item, "size": size,
             "height": height, "build": build, "fit": fit}
    return clean, errors


def parse_height_filter(raw):
    """Empty -> None, digits -> int, anything else -> ValueError."""
    raw = raw.strip()
    if raw == "":
        return None
    if not raw.isdigit():
        raise ValueError(raw)
    return int(raw)


# ---------------------------------------------------------------- timing
@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.context_processor
def inject_helpers():
    def load_ms():
        return round((time.perf_counter() - g.start) * 1000, 1)
    return {"load_ms": load_ms}


# ---------------------------------------------------------------- views
@app.route("/")
def browse():
    reviews = load_reviews()
    total = len(reviews)

    min_raw = request.args.get("min", "").strip()
    max_raw = request.args.get("max", "").strip()
    build = request.args.get("build", "").strip()
    if build not in BUILDS:
        build = ""

    filter_error = None
    lo = hi = None
    try:
        lo = parse_height_filter(min_raw)
        hi = parse_height_filter(max_raw)
        if lo is not None and hi is not None and lo > hi:
            filter_error = "The first height must be less than or equal to the second."
            lo = hi = None
    except ValueError:
        filter_error = "Enter heights as whole numbers in cm, like 160."
        lo = hi = None

    matches = [
        r for r in reviews
        if (lo is None or r["height"] >= lo)
        and (hi is None or r["height"] <= hi)
        and (not build or r["build"] == build)
    ]
    matches.reverse()  # newest first

    parts = []
    if lo is not None and hi is not None:
        parts.append(f"height {lo} to {hi} cm")
    elif lo is not None:
        parts.append(f"height {lo} cm or taller")
    elif hi is not None:
        parts.append(f"height up to {hi} cm")
    if build:
        parts.append(build)

    return render_template(
        "browse.html",
        reviews=matches, total=total, shown=len(matches),
        filter_active=bool(parts), criteria=", ".join(parts),
        filter_error=filter_error, min_raw=min_raw, max_raw=max_raw,
        build=build, builds=BUILDS,
    )


@app.route("/submit", methods=["GET", "POST"])
def submit():
    form, errors = {}, {}
    if request.method == "POST":
        form = request.form
        clean, errors = validate_review(form)
        if not errors:
            add_review(clean)
            return redirect(url_for("submitted"))
    return render_template(
        "submit.html", form=form, errors=errors, builds=BUILDS,
        build_guide=BUILD_GUIDE, fit_ratings=FIT_RATINGS,
        min_height=MIN_HEIGHT_CM, max_height=MAX_HEIGHT_CM,
    )


@app.route("/submitted")
def submitted():
    return render_template("submitted.html")


if __name__ == "__main__":
    app.run(debug=True)
