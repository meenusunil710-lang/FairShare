FairShare 🎯
Basic Details


Team Name: HackHer Duo

Team Members

Member 1: Meenu Sunil - College of Engineering Chengannur

Member 2: Norlida Zakariya - College of Engineering Chengannur

Hosted Project Link
https://fairshare-gtkr.onrender.com

Project Description

FairShare is a streamlined project management dashboard designed to take the chaos out of team collaboration. It allows users to create projects, break them down into specific modules, and assign team members to lead those tasks. The app calculates real-time progress based on task completion and generates professional summary reports.

The Problem statement

In group projects, it is often difficult to accurately track each member’s contributions, which can lead to unfair allocation of credit, confusion during report submission, and disputes over performance evaluation. Teams need a system that transparently records individual contributions, aggregates them, and generates a final report that reflects each member’s effort.

The Solution

Develop a web-based application that allows team members to log their tasks and contributions in real time. The system automatically tracks who did what, assigns weights or points to tasks, and generates a summary dashboard showing each member’s contribution. At the end, it produces a consolidated report that can be submitted along with the project, ensuring transparency and fair credit distribution.

Technical Details

Technologies/Components Used

For Software:

Languages used: Python

Frameworks used: Flask

Libraries used: 

Flask – Core web framework to handle routes, forms, and requests.
Flask-SQLAlchemy – ORM for managing SQLite database easily.
Flask-CORS – Allows your frontend (HTML/JS) to communicate with Flask APIs.
Werkzeug – Comes with Flask, handles routing and security.
Jinja2 – Templating engine (built into Flask) to render HTML pages dynamically.
Tools used: VS code,GitHub
For Hardware:

Main components: 

1. **Backend** – Flask and SQLite handle routes, logic, and store project, module, and member data.
2. **Frontend** – HTML, CSS, and Jinja2 templates display pages for projects, modules, member assignments, and the final report.
3. **Core Features** – Project and module management, contribution tracking, progress visualization, and final report generation.

Specifications:

Backend: Python 3 + Flask, handling routing, APIs, and business logic.
Database: SQLite3 managed via SQLAlchemy ORM for projects, modules, members, and contributions.
Frontend: HTML5, CSS3 (Flexbox & Grid), Jinja2 templates for dynamic content rendering.
Libraries/Extensions: Flask-CORS for API communication, optional Chart.js for dashboards.
Architecture: MVC pattern – Models (data), Views (templates), Controllers (Flask routes).
Deployment: Runs on local server for hackathon; scalable to cloud if needed.
Version Control: Git + GitHub for collaborative development.

Tools required: 

Python 3 – To run the Flask backend.
Flask – Web framework for building the server.
SQLite3 – Lightweight relational database.
VS Code – IDE for coding frontend and backend.
Git & GitHub – Version control and collaboration.
Web Browser – To run and test the web application

Features

List the key features of your project:
1.Solid Dashboard: A clean, high-contrast interface for managing multiple projects at once.
2.Progress Automation: Visual progress bars that update automatically as tasks are marked complete.
3.Team Assignment: Create team members and link them to specific project modules.
4.Activity Logs: A dedicated timeline for each task to track daily updates and hurdles.
5.Final Reports: A one-click, print-optimized summary of the entire project journey.
6.Reliable Database: Uses SQLite in WAL Mode to prevent "Database Locked" errors and ensure smooth performance

Implementation

For Software:
Installation
Create a virtual environment (optional but recommended)
python -m venv venv
Activate the virtual environment
On Windows:
venv\Scripts\activate
On Linux/Mac:
source venv/bin/activate
Install required Python libraries
pip install -r requirements.txt
Run
Start the Flask server
python app.py
Open a web browser and go to
http://127.0.0.1:5000

Project Documentation
For Software:
Screenshots (Add at least 3)
<img width="1914" height="870" alt="Screenshot 2026-02-28 092742" src="https://github.com/user-attachments/assets/07993632-d260-4d1d-a7ec-1fdabb3b26e1" />

Dashboard

<img width="1866" height="869" alt="Screenshot 2026-02-28 094840" src="https://github.com/user-attachments/assets/ca617a2a-e4c7-42a7-be2e-dd84752ce34d" />

Add member and modules

<img width="1846" height="800" alt="Screenshot 2026-02-28 094926" src="https://github.com/user-attachments/assets/577c2e84-2c19-4281-9bd4-c5cd260dba7c" />

Module complete

<img width="1822" height="909" alt="Screenshot 2026-02-28 095003" src="https://github.com/user-attachments/assets/aa53f028-2845-4e70-9958-7224ed7525a0" />

Final report

Diagrams
System Architecture:
User (Browser)
        │
        ▼
Frontend (HTML + CSS + Jinja2 Templates)
        │  HTTP Request
        ▼
Flask Backend (app.py)
        │  SQL Queries via SQLAlchemy
        ▼
SQLite Database (fairshare.db)
        ▲
        │  Data Response
        └───────────────


Application Workflow:
### **Application Workflow**

1. The user opens the FairShare application in a web browser.
2. The user creates a new project by entering project details and deadline.
3. The project is divided into modules/tasks and members are assigned.
4. Each member logs their progress or updates for assigned modules.
5. The system stores all updates in the database and calculates contribution percentages.
6. The dashboard displays real-time progress of modules and individual contributions.
7. Once the project is completed, the system generates a final report summarizing each member’s share of work.

**Caption:**
This workflow illustrates how FairShare manages project creation, task assignment, contribution tracking, progress visualization, and automated report generation in a structured and transparent manner.




Additional Documentation
For Web Projects with Backend:
API Documentation
Base URL: https://fairshare-gtkr.onrender.com

Endpoints
GET /projects

Description:
Retrieves the list of all projects with basic details.

Parameters:
None
Response:
 {
  "status": "success",
  "data": [
    {
      "project_id": 1,
      "project_name": "FairShare System",
      "deadline": "2026-03-10",
      "progress": 75
    }
  ]
}

### **POST /api/projects**
**Description:**
Creates a new project with a specified name and deadline.
**Request Body:**
```json
{
  "project_name": "Mini Project",
  "deadline": "2026-03-15"
}```
**Response:**
```json
{
  "status": "success",
  "message": "Project created successfully"
}```

---
### **POST /api/projects/{project_id}/modules**
**Description:**
Adds a new module/task to an existing project.
**Request Body:**
```json
{
  "module_name": "Frontend Development",
  "assigned_member": "Anu"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Module added successfully"
}
```
### **POST /api/modules/{module_id}/update**

**Description:**
Updates the progress of a specific module and logs contribution details.

**Request Body:**

```json
{
  "progress_percentage": 40,
  "update_note": "Completed UI layout"
}
```
**Response:**

```json
{
  "status": "success",
  "message": "Contribution updated successfully"
}
```

Project Demo

Video

https://drive.google.com/file/d/1o1UkSPH1Sezvg7s-cAfcd4pgsoQjbYdH/view?usp=drivesdk

Description:

FairShare – Smart Contribution Tracking for Group Projects
FairShare is a web-based application designed to ensure transparency and fairness in group projects. It allows teams to create projects, divide them into modules, assign members, and track individual contributions in real time. The system automatically calculates progress percentages and generates a final report summarizing each member’s share of work.
Built using Python (Flask) and SQLite for the backend, and HTML/CSS for the frontend, FairShare provides a simple yet effective solution to manage collaborative academic projects.
This demo showcases project creation, module assignment, contribution logging, dashboard visualization, and automated report generation.

AI Tools Used (Optional - For Transparency Bonus)
If you used AI tools during development, document them here for transparency:

Tool Used: GitHub Copilot, ChatGPT, Gemini

Purpose:

AI tools were used to accelerate development, generate boilerplate code, debug backend logic, structure database models, refine API endpoints, and improve UI layout consistency. They also assisted in optimizing queries, validating logic flow, and suggesting cleaner architectural patterns.

Examples:

Generated initial Flask project structure and route templates
Created REST API endpoints for project and module management
Assisted in debugging database relationship errors
Suggested improvements for contribution calculation logic
Provided UI structure and layout refinement ideas
Helped review and optimize code for better readability

Key Prompts Used

“Create a REST API endpoint for project creation in Flask.”
“Debug this Flask route that is not updating the database.”
“Design a database schema for tracking project contributions.”
“Optimize this SQLAlchemy query for faster performance.”
“Suggest improvements for a project contribution tracking system.”

Human Contributions:

The project idea, system design, and overall workflow were planned by the team. Database structure, backend logic, and frontend layout were implemented and integrated manually. Contribution calculations, report generation, testing, debugging, and final refinements were done by us to ensure the system works correctly and meets the project goals.


Team Contributions

Meenu Sunil:Backend 

Norlida Zakariya:Frontend and Backend planning
