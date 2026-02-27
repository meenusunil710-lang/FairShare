from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ----------------------------
# DATABASE CONNECTION
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect("fairshare.db")
    conn.row_factory = sqlite3.Row  # This allows us to use project['name'] instead of project[1]
    return conn

# ----------------------------
# DATABASE INITIALIZATION
# ----------------------------
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            deadline TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            assigned_member_id INTEGER,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_member_id) REFERENCES members(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS module_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            update_date TEXT,
            update_text TEXT,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ----------------------------
# ROUTES
# ----------------------------

@app.route("/")
def home():
    conn = get_db_connection()
    projects = conn.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return render_template("index.html", projects=projects)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["project_name"]
        deadline = request.form["deadline"]
        conn = get_db_connection()
        conn.execute("INSERT INTO projects (name, deadline) VALUES (?, ?)", (name, deadline))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template("create_project.html")

@app.route("/project/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    conn = get_db_connection()
    # Enabling foreign keys ensures that deleting a project deletes its modules/members too
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route("/project/<int:project_id>")
def project_modules(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    
    modules = conn.execute("""
        SELECT modules.*, members.name AS member_name 
        FROM modules 
        LEFT JOIN members ON modules.assigned_member_id = members.id 
        WHERE modules.project_id = ?
    """, (project_id,)).fetchall()

    members = conn.execute("SELECT * FROM members WHERE project_id = ?", (project_id,)).fetchall()
    
    # Calculate Progress
    total = len(modules)
    completed = sum(1 for m in modules if m['completed'])
    progress = int((completed / total) * 100) if total > 0 else 0
    
    conn.close()
    return render_template("project_modules.html", 
                           project=project, 
                           modules=modules, 
                           members=members, 
                           project_progress=progress)

@app.route("/project/<int:project_id>/add_member", methods=["POST"])
def add_member(project_id):
    name = request.form["member_name"]
    conn = get_db_connection()
    conn.execute("INSERT INTO members (name, project_id) VALUES (?, ?)", (name, project_id))
    conn.commit()
    conn.close()
    return redirect(url_for('project_modules', project_id=project_id))

@app.route("/project/<int:project_id>/add_module", methods=["POST"])
def add_module(project_id):
    name = request.form["module_name"]
    member_id = request.form["assigned_member"]
    conn = get_db_connection()
    conn.execute("INSERT INTO modules (name, project_id, assigned_member_id) VALUES (?, ?, ?)", 
                 (name, project_id, member_id))
    conn.commit()
    conn.close()
    return redirect(url_for('project_modules', project_id=project_id))

@app.route("/module/<int:module_id>")
def module_members(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    member = conn.execute("SELECT * FROM members WHERE id = ?", (module["assigned_member_id"],)).fetchone()
    updates = conn.execute("SELECT * FROM module_updates WHERE module_id = ? ORDER BY update_date DESC", (module_id,)).fetchall()
    conn.close()
    return render_template("module_members.html", module=module, member=member, updates=updates)

@app.route("/module/<int:module_id>/add_update", methods=["POST"])
def add_update(module_id):
    date = request.form["update_date"]
    text = request.form["update_text"]
    conn = get_db_connection()
    conn.execute("INSERT INTO module_updates (module_id, update_date, update_text) VALUES (?, ?, ?)", 
                 (module_id, date, text))
    conn.commit()
    conn.close()
    return redirect(url_for('module_members', module_id=module_id))

@app.route("/module/<int:module_id>/complete", methods=["POST"])
def complete_module(module_id):
    conn = get_db_connection()
    conn.execute("UPDATE modules SET completed = 1 WHERE id = ?", (module_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('module_members', module_id=module_id))

@app.route("/project/<int:project_id>/report")
def project_report(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    modules = conn.execute("""
        SELECT modules.*, members.name AS member_name 
        FROM modules 
        LEFT JOIN members ON modules.assigned_member_id = members.id 
        WHERE modules.project_id = ?
    """, (project_id,)).fetchall()
    
    updates = {}
    for m in modules:
        m_updates = conn.execute("SELECT * FROM module_updates WHERE module_id = ?", (m['id'],)).fetchall()
        updates[m['id']] = m_updates
        
    conn.close()
    return render_template("final_report.html", project=project, modules=modules, updates=updates)

if __name__ == "__main__":
    app.run(debug=True)