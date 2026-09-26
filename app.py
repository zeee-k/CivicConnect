import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.config.update(
    SECRET_KEY=os.environ.get("SESSION_SECRET", "civicconnect-academic-prototype-secret"),
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    UPLOAD_FOLDER=str(UPLOAD_FOLDER),
)

STATUSES = ["Pending", "Assigned", "In Progress", "Resolved"]
CATEGORIES = [
    "Road & Potholes",
    "Garbage & Waste Management",
    "Streetlights",
    "Water Supply",
    "Drainage & Sewerage",
    "Footpaths & Public Roads",
    "Traffic & Road Safety",
    "Public Toilets",
    "Parks & Public Spaces",
    "Stray Animal / Animal-related Civic Issue",
    "Illegal Dumping",
    "Other",
]
AREAS = [
    "Mira Road East",
    "Bhayandar East",
    "Bhayandar West",
    "Shanti Nagar",
    "Mira Road Station area",
    "Bhayandar Station area",
    "Golden Nest",
    "Bhayandar Phatak",
    "Beverly Park",
    "Kanakia",
    "Ramdev Park",
    "Pleasant Park",
]
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now_string():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def init_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('citizen', 'admin')),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            area TEXT NOT NULL,
            location TEXT NOT NULL,
            image_filename TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            admin_remark TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )

    admin = db.execute("SELECT id FROM users WHERE email = ?", ("admin@civicconnect.local",)).fetchone()
    if not admin:
        db.execute(
            "INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("CivicConnect Admin", "admin@civicconnect.local", generate_password_hash("Admin@123"), "admin", now_string()),
        )
    citizen = db.execute("SELECT id FROM users WHERE email = ?", ("citizen@civicconnect.local",)).fetchone()
    if not citizen:
        db.execute(
            "INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Demo Citizen", "citizen@civicconnect.local", generate_password_hash("Citizen@123"), "citizen", now_string()),
        )
        citizen = db.execute("SELECT id FROM users WHERE email = ?", ("citizen@civicconnect.local",)).fetchone()

    complaint_count = db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    if complaint_count == 0 and citizen:
        demo_complaints = [
            ("Road & Potholes", "Large pothole near Mira Road Station", "A large pothole is causing difficulty for two-wheelers and cars, especially during peak hours.", "Mira Road East", "Near Mira Road Railway Station", "In Progress"),
            ("Garbage & Waste Management", "Garbage accumulation near residential area", "Garbage has been accumulating near the roadside and requires collection.", "Bhayandar West", "Near a residential lane", "Pending"),
            ("Streetlights", "Non-functional streetlight", "A streetlight has not been working for several days, making the road difficult to use at night.", "Shanti Nagar", "Beside the community garden", "Assigned"),
            ("Drainage & Sewerage", "Waterlogging after rainfall", "Water accumulates on the roadside after heavy rainfall and affects pedestrians and vehicles.", "Bhayandar East", "Near the main market road", "In Progress"),
            ("Footpaths & Public Roads", "Damaged footpath", "A section of the footpath is damaged and difficult for pedestrians to use.", "Mira Road East", "Along the station approach road", "Resolved"),
            ("Streetlights", "Streetlight not functioning near residential road", "The streetlight near the residential area is not functioning properly at night.", "Golden Nest", "Near the residential entrance", "Pending"),
        ]
        db.executemany(
            """
            INSERT INTO complaints
            (user_id, category, title, description, area, location, status, admin_remark, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(citizen[0], *complaint, "", now_string(), now_string()) for complaint in demo_complaints],
        )
    db.commit()
    db.close()


def user_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        if g.user["role"] != "admin":
            flash("Admin access is required for that page.", "danger")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped_view


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.context_processor
def inject_template_values():
    return {"statuses": STATUSES, "categories": CATEGORIES, "areas": AREAS}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        error = None
        if not name or not email or not password or not confirm_password:
            error = "All fields are required."
        elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            error = "Enter a valid email address."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            try:
                get_db().execute(
                    "INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, 'citizen', ?)",
                    (name, email, generate_password_hash(password), now_string()),
                )
                get_db().commit()
            except sqlite3.IntegrityError:
                error = "An account with that email already exists."
        if error:
            flash(error, "danger")
        else:
            flash("Registration complete. You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user is None or not check_password_hash(user["password"], password):
            flash("Email or password is incorrect.", "danger")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name'].split()[0]}.", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


def complaint_counts(user_id=None):
    db = get_db()
    base = "SELECT status, COUNT(*) AS count FROM complaints"
    params = []
    if user_id:
        base += " WHERE user_id = ?"
        params.append(user_id)
    rows = db.execute(base + " GROUP BY status", params).fetchall()
    counts = {status: 0 for status in STATUSES}
    for row in rows:
        counts[row["status"]] = row["count"]
    counts["Total"] = sum(counts.values())
    return counts


@app.route("/dashboard")
@user_required
def dashboard():
    if g.user["role"] == "admin":
        return redirect(url_for("admin_dashboard"))
    recent = get_db().execute(
        "SELECT * FROM complaints WHERE user_id = ? ORDER BY id DESC LIMIT 5", (g.user["id"],)
    ).fetchall()
    return render_template("dashboard.html", counts=complaint_counts(g.user["id"]), recent=recent)


@app.route("/report", methods=("GET", "POST"))
@user_required
def report():
    if g.user["role"] != "citizen":
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        category = request.form.get("category", "")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        area = request.form.get("area", "")
        location = request.form.get("location", "").strip()
        image = request.files.get("image")
        error = None
        if category not in CATEGORIES:
            error = "Please choose a valid issue category."
        elif not title or len(title) < 5:
            error = "Please enter a descriptive issue title."
        elif not description or len(description) < 15:
            error = "Please add a little more detail to the description."
        elif area not in AREAS:
            error = "Please choose a valid area."
        elif not location:
            error = "Please enter the specific location."
        elif image and image.filename:
            extension = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
            if extension not in ALLOWED_EXTENSIONS:
                error = "Images must be JPG, JPEG, PNG or WEBP files."
        if error:
            flash(error, "danger")
        else:
            filename = None
            if image and image.filename:
                filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
                image.save(UPLOAD_FOLDER / filename)
            timestamp = now_string()
            get_db().execute(
                """
                INSERT INTO complaints
                (user_id, category, title, description, area, location, image_filename, status, admin_remark, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', '', ?, ?)
                """,
                (g.user["id"], category, title, description, area, location, filename, timestamp, timestamp),
            )
            get_db().commit()
            flash("Your issue was reported successfully and is now Pending review.", "success")
            return redirect(url_for("complaints"))
    return render_template("report.html")


@app.route("/complaints")
@user_required
def complaints():
    if g.user["role"] == "admin":
        return redirect(url_for("admin_complaints"))
    query = "SELECT * FROM complaints WHERE user_id = ?"
    params = [g.user["id"]]
    filters = {"category": request.args.get("category", ""), "status": request.args.get("status", ""), "area": request.args.get("area", "")}
    if filters["category"]:
        query += " AND category = ?"
        params.append(filters["category"])
    if filters["status"]:
        query += " AND status = ?"
        params.append(filters["status"])
    if filters["area"]:
        query += " AND area = ?"
        params.append(filters["area"])
    query += " ORDER BY id DESC"
    rows = get_db().execute(query, params).fetchall()
    return render_template("complaints.html", complaints=rows, filters=filters)


def get_complaint_or_404(complaint_id):
    complaint = get_db().execute(
        """
        SELECT complaints.*, users.name AS citizen_name, users.email AS citizen_email
        FROM complaints JOIN users ON users.id = complaints.user_id
        WHERE complaints.id = ?
        """,
        (complaint_id,),
    ).fetchone()
    if complaint is None:
        abort(404)
    return complaint


@app.route("/complaint/<int:complaint_id>")
@user_required
def complaint_detail(complaint_id):
    complaint = get_complaint_or_404(complaint_id)
    if g.user["role"] != "admin" and complaint["user_id"] != g.user["id"]:
        abort(403)
    return render_template("complaint_detail.html", complaint=complaint, is_admin=g.user["role"] == "admin")


@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    area_rows = db.execute("SELECT area, COUNT(*) AS count FROM complaints GROUP BY area ORDER BY count DESC").fetchall()
    category_rows = db.execute("SELECT category, COUNT(*) AS count FROM complaints GROUP BY category ORDER BY count DESC").fetchall()
    return render_template("admin_dashboard.html", counts=complaint_counts(), area_rows=area_rows, category_rows=category_rows)


@app.route("/admin/complaints")
@admin_required
def admin_complaints():
    query = """
        SELECT complaints.*, users.name AS citizen_name
        FROM complaints JOIN users ON users.id = complaints.user_id
        WHERE 1 = 1
    """
    params = []
    search = request.args.get("search", "").strip()
    filters = {"search": search, "category": request.args.get("category", ""), "status": request.args.get("status", ""), "area": request.args.get("area", "")}
    if search:
        query += " AND (complaints.title LIKE ? OR complaints.description LIKE ? OR users.name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    for key, column in (("category", "category"), ("status", "status"), ("area", "area")):
        if filters[key]:
            query += f" AND complaints.{column} = ?"
            params.append(filters[key])
    query += " ORDER BY complaints.id DESC"
    rows = get_db().execute(query, params).fetchall()
    return render_template("admin_complaints.html", complaints=rows, filters=filters)


@app.route("/admin/complaint/<int:complaint_id>", methods=("GET", "POST"))
@admin_required
def admin_complaint_detail(complaint_id):
    complaint = get_complaint_or_404(complaint_id)
    if request.method == "POST":
        status = request.form.get("status", "")
        remark = request.form.get("admin_remark", "").strip()
        if status not in STATUSES:
            flash("Please choose a valid status.", "danger")
        else:
            get_db().execute(
                "UPDATE complaints SET status = ?, admin_remark = ?, updated_at = ? WHERE id = ?",
                (status, remark, now_string(), complaint_id),
            )
            get_db().commit()
            flash("Complaint updated successfully.", "success")
            return redirect(url_for("admin_complaint_detail", complaint_id=complaint_id))
        complaint = get_complaint_or_404(complaint_id)
    return render_template("admin_complaint_detail.html", complaint=complaint, is_admin=True)


@app.errorhandler(403)
def forbidden(_error):
    return render_template("404.html", error_title="Access restricted", error_message="You do not have permission to view this page."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html", error_title="Page not found", error_message="The page you requested does not exist."), 404


@app.errorhandler(413)
def too_large(_error):
    flash("That image is too large. Please choose a file under 5 MB.", "danger")
    return redirect(url_for("report")), 413


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)