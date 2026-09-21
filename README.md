Here is the updated, accurate project documentation reflecting the current status, architecture, and technology stack of **FairShare**:

---

# FairShare 🎯

## Basic Details

### Hosted Project Link
- **Live Deployment:** `https://meenusunil.pythonanywhere.com/`

---

## Project Description
**FairShare** is a retro-styled project management dashboard designed to take the chaos out of team collaboration. It allows users to register and manage projects, break them down into priority-based modules, assign team members, track progress in real-time, and log timeline updates. Once completed, FairShare generates a print-optimized, consolidated project report reflecting total work distribution and project milestones.

---

## The Problem Statement
In collaborative and academic group projects, it is difficult to accurately track individual contributions and task progression. This often leads to unequal workload distribution, confusion during report submissions, and disputes over performance evaluation. Teams require a transparent, central system that records task ownership, timeline updates, completion status, and automated summary reports.

---

## The Solution
A web application where users can manage projects, recruit team members, assign modules with priority levels (High, Medium, Low), and log time-stamped activity updates. The system dynamically computes real-time completion percentages and produces an executive final report with one-click print readiness to ensure transparency and accountability.

---

## Technical Details

### Technologies Used

#### Backend & Database:
- **Python 3**: Core backend programming language.
- **Flask**: Web framework for routing, session management, forms, and API endpoints.
- **PostgreSQL (Neon Cloud)**: Production relational database for robust multi-user scalability and data integrity.
- **SQLite3**: Local lightweight fallback relational database with WAL mode.
- **psycopg2-binary**: PostgreSQL database adapter with dictionary cursor support.
- **python-dotenv**: Environment configuration and credentials management.
- **Werkzeug**: Secure password hashing (`scrypt`) and session authentication.
- **Gunicorn**: Production WSGI HTTP server.

#### Frontend:
- **HTML5 & CSS3**: Custom responsive layout using Flexbox and Grid.
- **Jinja2**: Server-side templating engine for dynamic rendering.
- **Design & Typography**: Retro pixel-art theme featuring Google Fonts (*'Press Start 2P'*), custom badge components, and smooth micro-animations.

#### Tools & DevOps:
- **VS Code**: Development environment.
- **Git & GitHub**: Source control and collaborative version tracking.
- **Neon**: Serverless Cloud PostgreSQL hosting.
- **Render / PythonAnywhere / Docker**: Cloud deployment platforms.

---

## Key Features

1. **User Authentication & Isolation**: Secure sign-up, sign-in, and session protection ensuring each user accesses their own dashboard and projects.
2. **Interactive Project Dashboard**: Real-time project metrics (Total Projects, Completed, Average Progress, Urgent Deadlines) with automated countdowns.
3. **Module & Task Management**: Categorize modules with priorities (*High, Medium, Low*), assign members, or keep tasks unassigned.
4. **Activity Timeline Logs**: Dedicated chronological updates per task to document daily milestones, blockers, and solutions.
5. **Dynamic Progress Tracking**: Auto-calculating visual progress bars reflecting project completion percentage.
6. **Print-Optimized Final Reports**: Executive summary detailing team members, module breakdowns, timeline entries, and completion ratios with built-in print formatting.
7. **Cloud Database Architecture**: Enterprise-grade PostgreSQL (Neon) with foreign-key constraints, cascading deletes, and local SQLite dual-mode support.

---

## System Architecture & Workflow

### System Architecture
```text
┌─────────────────────────────────────────────────────────────┐
│                    User Browser (Client)                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / HTTPS Requests
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application (app.py)                │
│  - Session Auth & Protected Routes                          │
│  - Business Logic & Progress Calculation                    │
│  - Jinja2 Template Rendering Engine                         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Database Queries (psycopg2 / sqlite3)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Relational Database                     │
│  - Production: Neon Cloud PostgreSQL                        │
│  - Local Dev: SQLite3 (fairshare.db)                        │
└─────────────────────────────────────────────────────────────┘
```

### Application Workflow
1. **Authentication**: User creates an account and logs into their private dashboard.
2. **Project Creation**: User creates a new project with a specified name and deadline.
3. **Team Recruitment & Task Setup**: User recruits team members and creates modules with assigned priorities.
4. **Execution & Updates**: Members log date-stamped progress entries and mark modules completed.
5. **Real-Time Visualization**: Dashboard metrics and module progress bars update dynamically.
6. **Final Report Generation**: One-click generation of a print-ready project audit report.

---

## Installation & Local Setup

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/FairShare.git
cd FairShare

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
SECRET_KEY=your-secret-key-here
```
*(If `DATABASE_URL` is omitted, FairShare will automatically use local SQLite `fairshare.db`)*

### 4. Run the Application
```bash
python app.py
```
Open `http://localhost:5000` in your web browser.

---

## API Documentation

### **GET `/api/projects`**
- **Description:** Retrieves all projects belonging to the authenticated user.
- **Response:**
```json
[
  {
    "id": 1,
    "name": "Website Redesign",
    "deadline": "2026-10-15",
    "progress": 75
  }
]
```

### **GET `/api/project/<id>/progress`**
- **Description:** Fetches progress statistics for a specific project.
- **Response:**
```json
{
  "total": 4,
  "completed": 3,
  "progress": 75
}
```

---

## AI Tools Used (For Transparency)

- **Tools Used:** GitHub Copilot, ChatGPT, Gemini, Antigravity AI Assistant.
- **Purpose:** 
  - Database schema design & PostgreSQL migration scripting.
  - Debugging database foreign key constraints and error handling.
  - Designing responsive retro pixel-art CSS styling and Jinja2 layout structure.
  - Structuring API endpoints and validation logic.

---

