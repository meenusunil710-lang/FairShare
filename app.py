from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ----------------------------
# DATABASE CONNECTION
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect("fairshare.db", timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

# ----------------------------
# DATABASE INITIALIZATION & MIGRATION
# ----------------------------
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create Tables
    c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, deadline TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, project_id INTEGER, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS modules (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, project_id INTEGER, assigned_member_id INTEGER, completed INTEGER DEFAULT 0, FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE, FOREIGN KEY (assigned_member_id) REFERENCES members(id))")
    c.execute("CREATE TABLE IF NOT EXISTS module_updates (id INTEGER PRIMARY KEY AUTOINCREMENT, module_id INTEGER, update_date TEXT, update_text TEXT, FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE)")
    
    # Migration: Add priority column if it doesn't exist
    try:
        c.execute("ALTER TABLE modules ADD COLUMN priority TEXT DEFAULT 'Medium'")
    except sqlite3.OperationalError:
        pass # Column already exists
        
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
    
    projects_with_info = []
    for project in projects:
        p_dict = dict(project)
        
        # --- COUNTDOWN LOGIC ---
        try:
            # Convert string date from DB to Python date object
            deadline_date = datetime.strptime(project['deadline'], '%Y-%m-%d').date()
            today = datetime.now().date()
            delta = (deadline_date - today).days
            
            if delta < 0:
                p_dict['days_left'] = "Overdue"
                p_dict['urgency'] = "high" # For CSS coloring
            elif delta == 0:
                p_dict['days_left'] = "Due Today"
                p_dict['urgency'] = "high"
            else:
                p_dict['days_left'] = f"{delta} days left"
                p_dict['urgency'] = "normal"
        except (ValueError, TypeError):
            p_dict['days_left'] = "No Date Set"
            p_dict['urgency'] = "none"

        # --- PROGRESS LOGIC ---
        modules = conn.execute("SELECT completed FROM modules WHERE project_id = ?", (project['id'],)).fetchall()
        total = len(modules)
        completed = sum(1 for m in modules if m['completed'])
        p_dict['progress'] = int((completed / total) * 100) if total > 0 else 0
        
        projects_with_info.append(p_dict)
        
    conn.close()
    return render_template("index.html", projects=projects_with_info)

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

@app.route("/project/<int:project_id>")
def project_modules(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    
    # Fetch modules with member names and priorities
    modules = conn.execute("""
        SELECT m.*, mem.name as member_name 
        FROM modules m 
        LEFT JOIN members mem ON m.assigned_member_id = mem.id 
        WHERE m.project_id = ?
    """, (project_id,)).fetchall()
    
    members = conn.execute("SELECT * FROM members WHERE project_id = ?", (project_id,)).fetchall()
    
    # Summary progress for the page header
    total = len(modules)
    completed = sum(1 for m in modules if m['completed'])
    progress = int((completed / total) * 100) if total > 0 else 0
    
    conn.close()
    return render_template("project_modules.html", project=project, modules=modules, members=members, progress=progress)

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
    priority = request.form.get("priority", "Medium") # Safeguard with .get()
    
    conn = get_db_connection()
    conn.execute("INSERT INTO modules (name, project_id, assigned_member_id, priority) VALUES (?, ?, ?, ?)", 
                 (name, project_id, member_id, priority))
    conn.commit()
    conn.close()
    return redirect(url_for('project_modules', project_id=project_id))

@app.route("/module/<int:module_id>")
def module_members(module_id):
    conn = get_db_connection()
    module = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    member = conn.execute("SELECT * FROM members WHERE id = ?", (module["assigned_member_id"],)).fetchone()
    updates = conn.execute("SELECT * FROM module_updates WHERE module_id = ? ORDER BY update_date DESC", (module_id,)).fetchall()
    
    # NEW: Fetch all members of this project so we can reassign the task
    all_members = conn.execute("SELECT * FROM members WHERE project_id = ?", (module['project_id'],)).fetchall()
    
    conn.close()
    return render_template("module_members.html", 
                           module=module, 
                           member=member, 
                           updates=updates, 
                           all_members=all_members) # Send them to the template

@app.route("/module/<int:module_id>/add_update", methods=["POST"])
def add_update(module_id):
    date, text = request.form["update_date"], request.form["update_text"]
    conn = get_db_connection()
    conn.execute("INSERT INTO module_updates (module_id, update_date, update_text) VALUES (?, ?, ?)", (module_id, date, text))
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

@app.route("/project/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    conn = get_db_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    finally:
        conn.close()
    return redirect(url_for('home'))

@app.route("/project/<int:project_id>/report")
def project_report(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    modules = conn.execute("""
        SELECT m.*, mem.name as member_name 
        FROM modules m 
        LEFT JOIN members mem ON m.assigned_member_id = mem.id 
        WHERE m.project_id = ?
    """, (project_id,)).fetchall()
    
    total_tasks = len(modules)
    completed_tasks = sum(1 for m in modules if m['completed'])
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    updates = {}
    for m in modules:
        m_updates = conn.execute("SELECT * FROM module_updates WHERE module_id = ? ORDER BY update_date ASC", (m['id'],)).fetchall()
        updates[m['id']] = m_updates
        
    conn.close()
    return render_template("final_report.html", 
                           project=project, 
                           modules=modules, 
                           updates=updates, 
                           progress=progress,
                           total=total_tasks,
                           completed=completed_tasks)
@app.route("/module/<int:module_id>/edit", methods=["POST"])
def edit_module(module_id):
    name = request.form["module_name"]
    member_id = request.form["assigned_member"]
    priority = request.form["priority"]
    
    conn = get_db_connection()
    conn.execute("""
        UPDATE modules 
        SET name = ?, assigned_member_id = ?, priority = ? 
        WHERE id = ?
    """, (name, member_id, priority, module_id))
    conn.commit()
    conn.close()
    return redirect(url_for('module_members', module_id=module_id))
@app.route("/project/<int:project_id>/delete_task/<int:module_id>", methods=["POST"])
def delete_task(project_id, module_id):
    conn = get_db_connection()
    try:
        # PRAGMA ensures that if you delete a task, its updates go with it
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('project_modules', project_id=project_id))

if __name__ == "__main__":
    app.run(debug=True)