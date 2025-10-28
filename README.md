# COSC4353_Project
:D  
Idk, I'm confuzzled
------------------------
How to run:
Note: These commands only work for WINDOWS OS

To run in vite (frontend):
npm install (install dependencies)
npm run dev (view dev site)

To run python Flask backend:
Navigate to backend folder or wherever app.py file of backend is located
1) python -m venv venv
2) .\\venv\\Scripts\\activate
    2a) If you do not have dependencies already installed:
        pip install Flask Flask-Cors "pydantic[email]" pytest pytest-cov firebase-admin

        To check; Will show all dependencies installed in curr. env.:
        pip list
3) .\\venv\\Scripts\\python.exe app.py

Login:

    Admin: 
        admin@example.com
        AdminPassword1

    User:
        volunteer@example.com
        Password1

To run unit tests:
1) pytest (auto discover/run unit tests)

Code coverage report:
- Quick Summary:
    pytest --cov=app
- HTML Detailed:
    pytest --cov=app --cov-report=html
------------------------------------------------------------------------------
App Description:
A non-profit organization has requested to build a software application that will help manage and optimize their volunteer activities. The application should help the organization efficiently allocate volunteers to different events and tasks based on their preferences, skills, and availability. The application should consider the following criteria:
    -   Volunteer’s location
    -   Volunteer’s skills and preferences
    -   Volunteer’s availability
    -   Event requirements and location
    -   Task urgency and priority

The software must include the following components:
    -   Login (Allow volunteers and administrators to register if not already registered)
    -   User Registration (Initially only username and password, followed by email verification)
    -   User Profile Management (After registration, users should log in to complete their profile, including location, skills, preferences, and availability)
    -   Event Management (Administrators can create and manage events, specifying required skills, location, and urgency)
    -   Volunteer Matching (A module that matches volunteers to events/tasks based on their profiles and the event requirements)
    -   Notification System (Send notifications to volunteers for event assignments, updates, and reminders)
    -   Volunteer History (Track volunteer participation history and performance)
