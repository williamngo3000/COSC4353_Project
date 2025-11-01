#volunteer management system 

#overview 
this backend (Flask + SQLite) powers the Volunteer Management website 
- User registeration and login 
- Event Listing 
- user profiles and volunteer history 
- integration with the react frontend 

#Tech stack 
- Backend framework - Flask (Python) 
- Database - SQLite 
- ORM - SQLAlchemy 
- Frontend - React 
- Api Hosting dev- flask local server on http://127.0.01:5502 
-
-#Backend/
 app2.py # Flask app entry point
 models.py # Database models (SQLAlchemy)
 volunteer.db # SQLite database
 instance/volunteer.db# (alternate db path)
 venv/ # Python virtual environment
 requirements.txt # Dependencies

#activate virtual environment 
-python3 -m venv venv 
source venv/bin/activate 

#install dependencies 
- pip install flask flask_sqlalchemy flask_cors werkzeug 
#initialize and run the backend 
- python3 app2.py 
#expected output 
Database initialized at: /Users/melisaunlu/COSC4353_Project/Backend/volunteer.db
 * Serving Flask app 'app2'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5002
Press CTRL+C to quit
 * Restarting with stat
Database initialized at: /Users/melisaunlu/COSC4353_Project/Backend/volunteer.db
 * Debugger is active!
 * Debugger PIN: 391-812-903
127.0.0.1 - - [30/Oct/2025 23:47:10] "GET /api/test HTTP/1.1" 200 -
