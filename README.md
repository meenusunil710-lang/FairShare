 FairShare 
--• What the project is?
FairShare is a streamlined project management dashboard designed to take the chaos out of team collaboration. It allows users to create projects, break them down into specific modules, and assign team members to lead those tasks. The app calculates real-time progress based on task completion and generates professional summary reports.

--• What problem does it solve?
1. Tracking who’s doing what

In a normal group project, you assign tasks via chat or notes. People forget, duplicates happen, or someone slacks off.

FairShare clearly assigns modules to members, so everyone knows exactly what they are responsible for.

2. Monitoring progress

Instead of manually checking with everyone, the app automatically calculates overall project progress as modules are completed.

Shows percentage complete dynamically, so you know if you’re on track.

3. Handling deadlines

Each project can have a deadline.

FairShare flags modules that are incomplete as deadlines approach.

Allows reassigning modules if the original member cannot finish, so the project doesn’t stall.

4. Keeping detailed updates

Members can add updates per module: what was done, what’s pending.

The final report compiles all updates, making it easy to see contributions and work history for grading or review.

5. Avoiding chaos

Instead of scattered spreadsheets, WhatsApp messages, or sticky notes, the project’s progress is centralized in one app.

Reduces confusion and ensures accountability.

--• Where is it used?
FairShare is primarily designed for educational group projects, helping students collaborate efficiently. It’s perfect for:

College or School Projects

Divide work among group members.

Track which student is responsible for each module.

Automatically see overall progress of the project.

Hackathons and Academic Competitions

Quickly assign modules to team members.

Monitor progress and make sure deadlines are met.

Study Groups & Collaborative Learning

Students working together on coding, research, or design projects.

Keep records of contributions and updates for each part of the project.

⚠️ Note: While it could technically be used for small teams in companies, it’s optimized for educational purposes, where tracking student contributions and deadlines matters most.


--• How to install/run it
Clone & Navigate:


git clone https://github.com/meenusunil710-lang/FairShare.git
cd FairShare
Install Requirements:


pip install flask
Launch the App:

python app.py
Access:
Open your browser and go to http://127.0.0.1:5000.

--• Features
Solid Dashboard: A clean, high-contrast interface for managing multiple projects at once.

Progress Automation: Visual progress bars that update automatically as tasks are marked complete.

Team Assignment: Create team members and link them to specific project modules.

Activity Logs: A dedicated timeline for each task to track daily updates and hurdles.

Final Reports: A one-click, print-optimized summary of the entire project journey.

Reliable Database: Uses SQLite in WAL Mode to prevent "Database Locked" errors and ensure smooth performance.

--• Technologies used
Backend: Python 3 + Flask (Web Framework)

Database: SQLite3 (Relational Database)

Frontend: HTML5, CSS3 (Solid Flexbox & Grid layout)

Font: Plus Jakarta Sans (Modern high-readability typeface)
--• Structure
FairShare/
│
├─ app.py                   <-- Main Flask application
├─ fairshare.db             <-- SQLite database (auto-created)
├─ requirements.txt         <-- Python dependencies
├─ venv/                    <-- Virtual environment (optional to keep)
│
├─ templates/               <-- HTML templates
│   ├─ index.html            <-- Home page (list of projects)
│   ├─ create_project.html   <-- Form to create new project (with deadline)
│   ├─ project_modules.html  <-- View project modules, progress bar
│   ├─ module_members.html   <-- Module details, assigned member, updates
│   ├─ final_report.html     <-- Project final report
│
└─ static/                  <-- CSS / JS / images
    ├─ style.css             <-- Main CSS file

--• Author info
Developed by: HackHer Duo(Meenu Sunil- Backend+Database ,Norlida Zakariya - Frontend+Templates)
            