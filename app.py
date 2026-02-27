from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ----------------------------
# DATABASE CONNECTION
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect("fairshare.db")
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn

# ----------------------------
# DATABASE INITIALIZATION
# ----------------------------
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Projects table
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    # Members table
    c.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Modules table
    c.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            assigned_member_id INTEGER,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assigned_member_id) REFERENCES members(id)
        )
    """)

    # Module updates table
    c.execute("""
        CREATE TABLE IF NOT EXISTS module_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            update_date TEXT,
            update_text TEXT,
            FOREIGN KEY (module_id) REFERENCES modules(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    conn = get_db_connection()
    projects = conn.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return render_template("index.html", projects=projects)

# ----------------------------
# CREATE PROJECT
# ----------------------------
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["project_name"]
        conn = get_db_connection()
        conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("create_project.html")

# ----------------------------
# PROJECT MODULES (with project-level progress)
# ----------------------------
@app.route("/project/<int:project_id>")
def project_modules(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()

    # Fetch modules with assigned member names
    modules = conn.execute("""
        SELECT modules.id, modules.name, modules.project_id, members.name AS member_name, modules.completed
        FROM modules
        LEFT JOIN members ON modules.assigned_member_id = members.id
        WHERE modules.project_id = ?
    """, (project_id,)).fetchall()
    modules = [dict(m) for m in modules]

    # Calculate project-level progress
    total_modules = len(modules)
    completed_modules = sum(1 for m in modules if m['completed'])
    project_progress = int((completed_modules / total_modules) * 100) if total_modules else 0

    # Fetch members for module assignment dropdown
    members = conn.execute("SELECT id, name FROM members WHERE project_id = ?", (project_id,)).fetchall()
    conn.close()

    return render_template("project_modules.html",
                           project=project,
                           modules=modules,
                           members=members,
                           project_progress=project_progress)

# ----------------------------
# ADD MEMBER
# ----------------------------
@app.route("/project/<int:project_id>/add_member", methods=["POST"])
def add_member(project_id):
    name = request.form["member_name"]
    conn = get_db_connection()
    conn.execute("INSERT INTO members (name, project_id) VALUES (?, ?)", (name, project_id))
    conn.commit()
    conn.close()
    return redirect(f"/project/{project_id}")

# ----------------------------
# ADD MODULE
# ----------------------------
@app.route("/project/<int:project_id>/add_module", methods=["POST"])
def add_module(project_id):
    name = request.form["module_name"]
    assigned_member_id = request.form["assigned_member"]
    conn = get_db_connection()
    conn.execute("INSERT INTO modules (name, project_id, assigned_member_id) VALUES (?, ?, ?)",
                 (name, project_id, assigned_member_id))
    conn.commit()
    conn.close()
    return redirect(f"/project/{project_id}")

# ----------------------------
# MODULE PAGE: MEMBER + UPDATES
# ----------------------------
@app.route("/module/<int:module_id>")
def module_members(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    member = conn.execute("SELECT * FROM members WHERE id = ?", (module["assigned_member_id"],)).fetchone()
    updates = conn.execute("""
        SELECT * FROM module_updates
        WHERE module_id = ?
        ORDER BY update_date ASC
    """, (module_id,)).fetchall()
    conn.close()
    return render_template("module_members.html", module=module, member=member, updates=updates)

# ----------------------------
# ADD UPDATE TO MODULE
# ----------------------------
@app.route("/module/<int:module_id>/add_update", methods=["POST"])
def add_update(module_id):
    update_date = request.form["update_date"]
    update_text = request.form["update_text"]
    conn = get_db_connection()
    conn.execute("INSERT INTO module_updates (module_id, update_date, update_text) VALUES (?, ?, ?)",
                 (module_id, update_date, update_text))
    conn.commit()
    conn.close()
    return redirect(f"/module/{module_id}")

# ----------------------------
# MARK MODULE COMPLETE
# ----------------------------
@app.route("/module/<int:module_id>/complete", methods=["POST"])
def complete_module(module_id):
    conn = get_db_connection()
    conn.execute("UPDATE modules SET completed = 1 WHERE id = ?", (module_id,))
    conn.commit()
    conn.close()
    return redirect(f"/module/{module_id}")

# ----------------------------
# FINAL REPORT
# ----------------------------
@app.route("/project/<int:project_id>/report")
def project_report(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()

    # Fetch all modules with assigned member names
    modules = conn.execute("""
        SELECT modules.id, modules.name, modules.completed, members.name AS member_name
        FROM modules
        LEFT JOIN members ON modules.assigned_member_id = members.id
        WHERE modules.project_id = ?
    """, (project_id,)).fetchall()

    # Fetch all updates grouped by module
    updates = {}
    for module in modules:
        module_updates = conn.execute("""
            SELECT update_date, update_text
            FROM module_updates
            WHERE module_id = ?
            ORDER BY update_date ASC
        """, (module['id'],)).fetchall()
        updates[module['id']] = module_updates

    conn.close()
    return render_template("final_report.html",
                           project=project,
                           modules=modules,
                           updates=updates)

# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)