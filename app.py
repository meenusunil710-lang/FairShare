from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "fairshare.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")


# ----------------------------
# DATABASE ADAPTER
# ----------------------------
class PgConnectionWrapper:
    """Wraps a psycopg2 connection to provide a sqlite3-compatible interface."""
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def _convert_query(self, sql):
        # Convert ? placeholders to %s for PostgreSQL
        return sql.replace("?", "%s")

    def execute(self, sql, params=None):
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        formatted_sql = self._convert_query(sql)
        if params is not None:
            cur.execute(formatted_sql, params)
        else:
            cur.execute(formatted_sql)
        return cur

    def cursor(self):
        return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()


def get_db_connection():
    if DATABASE_URL and HAS_PSYCOPG2:
        conn = psycopg2.connect(DATABASE_URL)
        return PgConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def init_db():
    if DATABASE_URL and HAS_PSYCOPG2:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                deadline TEXT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS modules (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                assigned_member_id INTEGER REFERENCES members(id) ON DELETE SET NULL,
                completed INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'Medium'
            );
            CREATE TABLE IF NOT EXISTS module_updates (
                id SERIAL PRIMARY KEY,
                module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
                update_date TEXT,
                update_text TEXT
            );
        """)
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                email    TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                deadline TEXT,
                user_id  INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                name               TEXT NOT NULL,
                project_id         INTEGER,
                assigned_member_id INTEGER,
                completed          INTEGER DEFAULT 0,
                priority           TEXT DEFAULT 'Medium',
                FOREIGN KEY (project_id)         REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_member_id) REFERENCES members(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS module_updates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id   INTEGER,
                update_date TEXT,
                update_text TEXT,
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
            )
        """)
        migrations = [
            "ALTER TABLE modules ADD COLUMN priority TEXT DEFAULT 'Medium'",
            "ALTER TABLE projects ADD COLUMN user_id INTEGER",
        ]
        for m in migrations:
            try:
                c.execute(m)
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()


init_db()

# ----------------------------
# AUTH HELPERS
# ----------------------------
def login_required(f):
    """Decorator — redirects to login if not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def current_user():
    """Returns the logged-in user row, or None."""
    if "user_id" not in session:
        return None
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return user

def owns_project(project_id):
    """Returns True if the logged-in user owns this project."""
    conn = get_db_connection()
    project = conn.execute(
        "SELECT user_id FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    conn.close()
    if not project:
        return False
    # Allow if user_id is NULL (legacy data) or matches session
    return project["user_id"] is None or project["user_id"] == session.get("user_id")

def get_project_progress(conn, project_id):
    """Helper — returns (total, completed, progress%) for a project."""
    modules = conn.execute(
        "SELECT completed FROM modules WHERE project_id = ?", (project_id,)
    ).fetchall()
    total = len(modules)
    completed = sum(1 for m in modules if m["completed"])
    progress = int((completed / total) * 100) if total > 0 else 0
    return total, completed, progress

# ----------------------------
# AUTH ROUTES
# ----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        name     = request.form["name"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("signup.html")

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        hashed = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed)
        )
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------------------------
# MAIN ROUTES
# ----------------------------
@app.route("/")
@login_required
def home():
    conn = get_db_connection()
    # Only show THIS user's projects
    projects = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? OR user_id IS NULL ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()

    projects_with_info = []
    for project in projects:
        p_dict = dict(project)

        # Countdown logic
        try:
            deadline_date = datetime.strptime(project["deadline"], "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = (deadline_date - today).days
            if delta < 0:
                p_dict["days_left"] = "Overdue"
                p_dict["urgency"]   = "high"
            elif delta == 0:
                p_dict["days_left"] = "Due Today"
                p_dict["urgency"]   = "high"
            else:
                p_dict["days_left"] = f"{delta} days left"
                p_dict["urgency"]   = "normal"
        except (ValueError, TypeError):
            p_dict["days_left"] = "No Date Set"
            p_dict["urgency"]   = "none"

        _, _, progress = get_project_progress(conn, project["id"])
        p_dict["progress"] = progress
        projects_with_info.append(p_dict)

    conn.close()
    return render_template("index.html", projects=projects_with_info, user_name=session.get("user_name"))


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name     = request.form.get("project_name", "").strip()
        deadline = request.form.get("deadline")
        if not name:
            flash("Project name is required.", "error")
            return render_template("create_project.html", user_name=session.get("user_name"))
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO projects (name, deadline, user_id) VALUES (?, ?, ?)",
            (name, deadline, session["user_id"])
        )
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    return render_template("create_project.html", user_name=session.get("user_name"))


@app.route("/project/<int:project_id>")
@login_required
def project_modules(project_id):
    if not owns_project(project_id):
        return redirect(url_for("home"))

    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for("home"))

    modules  = conn.execute("""
        SELECT m.*, mem.name as member_name
        FROM modules m
        LEFT JOIN members mem ON m.assigned_member_id = mem.id
        WHERE m.project_id = ?
        ORDER BY CASE m.priority
            WHEN 'High'   THEN 1
            WHEN 'Medium' THEN 2
            ELSE 3
        END, m.completed ASC
    """, (project_id,)).fetchall()
    members  = conn.execute("SELECT * FROM members WHERE project_id = ?", (project_id,)).fetchall()
    _, _, progress = get_project_progress(conn, project_id)
    conn.close()

    return render_template(
        "project_modules.html",
        project=project,
        modules=modules,
        members=members,
        progress=progress,
        user_name=session.get("user_name")
    )


@app.route("/project/<int:project_id>/add_member", methods=["POST"])
@login_required
def add_member(project_id):
    if not owns_project(project_id):
        return redirect(url_for("home"))
    name = request.form.get("member_name", "").strip()
    if name:
        conn = get_db_connection()
        conn.execute("INSERT INTO members (name, project_id) VALUES (?, ?)", (name, project_id))
        conn.commit()
        conn.close()
    return redirect(url_for("project_modules", project_id=project_id))


@app.route("/project/<int:project_id>/add_module", methods=["POST"])
@login_required
def add_module(project_id):
    if not owns_project(project_id):
        return redirect(url_for("home"))

    name = request.form.get("module_name", "").strip()
    if not name:
        flash("Module name is required.", "error")
        return redirect(url_for("project_modules", project_id=project_id))

    assigned_member = request.form.get("assigned_member") or request.form.get("member_id")
    member_id = None
    if assigned_member and str(assigned_member).strip() not in ("0", "", "None"):
        try:
            member_id = int(assigned_member)
        except ValueError:
            member_id = None

    priority = request.form.get("priority", "Medium")
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO modules (name, project_id, assigned_member_id, priority) VALUES (?, ?, ?, ?)",
        (name, project_id, member_id, priority)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("project_modules", project_id=project_id))


@app.route("/module/<int:module_id>")
@login_required
def module_members(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not module or not owns_project(module["project_id"]):
        conn.close()
        return redirect(url_for("home"))
    member = None
    if module["assigned_member_id"]:
        member = conn.execute("SELECT * FROM members WHERE id = ?", (module["assigned_member_id"],)).fetchone()
    updates = conn.execute(
        "SELECT * FROM module_updates WHERE module_id = ? ORDER BY update_date DESC", (module_id,)
    ).fetchall()
    all_members = conn.execute(
        "SELECT * FROM members WHERE project_id = ?", (module["project_id"],)
    ).fetchall()
    conn.close()
    return render_template(
        "module_members.html",
        module=module,
        member=member,
        updates=updates,
        all_members=all_members,
        user_name=session.get("user_name")
    )


@app.route("/module/<int:module_id>/add_update", methods=["POST"])
@login_required
def add_update(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT project_id FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not module or not owns_project(module["project_id"]):
        conn.close()
        return redirect(url_for("home"))
    date = request.form.get("update_date") or datetime.now().strftime("%Y-%m-%d")
    text = request.form.get("update_text", "").strip()
    if text:
        conn.execute(
            "INSERT INTO module_updates (module_id, update_date, update_text) VALUES (?, ?, ?)",
            (module_id, date, text)
        )
        conn.commit()
    conn.close()
    return redirect(url_for("module_members", module_id=module_id))


@app.route("/module/<int:module_id>/complete", methods=["POST"])
@login_required
def complete_module(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT project_id FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not module or not owns_project(module["project_id"]):
        conn.close()
        return redirect(url_for("home"))
    conn.execute("UPDATE modules SET completed = 1 WHERE id = ?", (module_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("module_members", module_id=module_id))


@app.route("/module/<int:module_id>/edit", methods=["POST"])
@login_required
def edit_module(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT project_id FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not module or not owns_project(module["project_id"]):
        conn.close()
        return redirect(url_for("home"))
    name = (request.form.get("module_name") or request.form.get("name") or "").strip()
    if not name:
        conn.close()
        flash("Module name is required.", "error")
        return redirect(url_for("module_members", module_id=module_id))

    assigned_member = request.form.get("assigned_member") or request.form.get("member_id")
    member_id = None
    if assigned_member and str(assigned_member).strip() not in ("0", "", "None"):
        try:
            member_id = int(assigned_member)
        except ValueError:
            member_id = None

    priority = request.form.get("priority", "Medium")
    conn.execute(
        "UPDATE modules SET name = ?, assigned_member_id = ?, priority = ? WHERE id = ?",
        (name, member_id, priority, module_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("module_members", module_id=module_id))


@app.route("/project/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    if not owns_project(project_id):
        return redirect(url_for("home"))
    conn = get_db_connection()
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/project/<int:project_id>/delete_task/<int:module_id>", methods=["POST"])
@login_required
def delete_task(project_id, module_id):
    if not owns_project(project_id):
        return redirect(url_for("home"))
    conn = get_db_connection()
    conn.execute("DELETE FROM modules WHERE id = ? AND project_id = ?", (module_id, project_id))
    conn.commit()
    conn.close()
    return redirect(url_for("project_modules", project_id=project_id))


@app.route("/project/<int:project_id>/report")
@login_required
def project_report(project_id):
    if not owns_project(project_id):
        return redirect(url_for("home"))
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    modules  = conn.execute("""
        SELECT m.*, mem.name as member_name
        FROM modules m
        LEFT JOIN members mem ON m.assigned_member_id = mem.id
        WHERE m.project_id = ?
    """, (project_id,)).fetchall()

    total, completed, progress = get_project_progress(conn, project_id)

    updates = {}
    for m in modules:
        updates[m["id"]] = conn.execute(
            "SELECT * FROM module_updates WHERE module_id = ? ORDER BY update_date ASC", (m["id"],)
        ).fetchall()

    conn.close()
    return render_template(
        "final_report.html",
        project=project,
        modules=modules,
        updates=updates,
        progress=progress,
        total=total,
        completed=completed,
        user_name=session.get("user_name")
    )


# ----------------------------
# API ROUTES (JSON) — groundwork for decoupled frontend later
# ----------------------------
@app.route("/api/projects")
@login_required
def api_projects():
    conn = get_db_connection()
    projects = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    result = []
    for p in projects:
        _, _, progress = get_project_progress(conn, p["id"])
        result.append({
            "id":       p["id"],
            "name":     p["name"],
            "deadline": p["deadline"],
            "progress": progress,
        })
    conn.close()
    return jsonify(result)


@app.route("/api/project/<int:project_id>/progress")
@login_required
def api_project_progress(project_id):
    if not owns_project(project_id):
        return jsonify({"error": "Unauthorized"}), 403
    conn = get_db_connection()
    total, completed, progress = get_project_progress(conn, project_id)
    conn.close()
    return jsonify({"total": total, "completed": completed, "progress": progress})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
