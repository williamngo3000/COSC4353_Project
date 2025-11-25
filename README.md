># **COSC4353_Project**
:D  
Idk, I'm confuzzled
Note: Delete volunteer.db to prevent extra data or whatever; Essentially so a new database is made at all times

------
How to run:  
Note: These commands only work for WINDOWS OS

To run in vite (frontend):
- python -m venv venv
- .\venv\scripts\activate
- npm install (install dependencies)
- npm run dev (view dev site)
-----

>## To run python Flask backend:

1) Navigate to backend folder or wherever app.py file of backend is located
    -   cd .\backend\
2) python -m venv venv
3) .\venv\Scripts\activate  
    3a) If you do not have dependencies already installed:
        <br>
        ```
        pip install -r requirements.txt
        ```
        <br>
        To check; Will show all dependencies installed in curr. env.: <br>
        pip list

4) .\\venv\\Scripts\\python.exe app.py
-----
    Login:

        Admin: 
            admin@example.com
            AdminPassword1

        User:
            volunteer@example.com
            Password1
-----

>## To run SQLite database:

Prerequisite: Run python flask backend first, or at least the instructions

Command:

```
.\\venv\\scripts\\python.exe app2.py
```

-----

>### To run unit tests:

1) pytest (auto discover/run unit tests)
Code coverage report:
- Quick Summary: 
<br>
```
    pytest --cov=app
```
<br>

- HTML Detailed:
```
    pytest --cov=app --cov-report=html
```


2) coverage run -m unittest

```

App Description: A non-profit organization has requested to build a software application that will help manage and optimize their volunteer activities. The application should help the organization efficiently allocate volunteers to different events and tasks based on their preferences, skills, and availability. The application should consider the following criteria:
- Volunteer’s location
- Volunteer’s skills and preferences
- Volunteer’s availability
- Event requirements and location
- Task urgency and priority

The software must include the following components: 
- Login (Allow volunteers and administrators to register if not already registered) 
- User Registration (Initially only username and password, followed by email verification) 
- User Profile Management (After registration, users should log in to complete their profile, including location, skills, preferences, and availability) 
- Event Management (Administrators can create and manage events, specifying required skills, location, and urgency) 
- Volunteer Matching (A module that matches volunteers to events/tasks based on their profiles and the event requirements) 
- Notification System (Send notifications to volunteers for event assignments, updates, and reminders) 
- Volunteer History (Track volunteer participation history and performance)

```