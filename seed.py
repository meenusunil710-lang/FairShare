import sqlite3
from datetime import datetime, timedelta

def seed():
    conn = sqlite3.connect("fairshare.db")
    # 1. Create a "Crisis" Project (Overdue)
    conn.execute("INSERT INTO projects (name, deadline) VALUES (?, ?)", 
                 ("Legacy System Migration", "2024-01-01"))
    
    # 2. Create the "Hackathon" Project (On Track)
    deadline = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    conn.execute("INSERT INTO projects (name, deadline) VALUES (?, ?)", 
                 ("FairShare Final Launch", deadline))
    
    conn.commit()
    conn.close()
    print("Database seeded with demo data!")

seed()