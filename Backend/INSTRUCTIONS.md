# Backend Setup and Testing Instructions

This guide provides all the necessary steps to set up, run, and test the Python backend.



**Part 1: Initial Setup (Only needs to be done once)**

Open Terminal in Backend Folder:

Navigate your terminal (like PowerShell or Command Prompt) to your backend project folder (the one containing app.py or whatever the name of your backend file is).



Create Virtual Environment:

Run the command for your operating system to create a virtual environment folder named venv.



For Windows:

python -m venv venv



For macOS/Linux:

python3 -m venv venv



Activate the Virtual Environment:

You must activate the environment before installing packages.



For Windows:

.\\venv\\Scripts\\activate



For macOS/Linux:

source venv/bin/activate



(You will see (venv) at the beginning of your terminal prompt when it's active.)



Install All Dependencies:

With the virtual environment active, run the following command to install Flask, Pytest, and all other required packages.



pip install Flask Flask-Cors "pydantic[email]" pytest pytest-cov



**Part 2: Running the Backend Server (Do this every time you want to run the app)**

Open Terminal and Activate Environment:

Open a new terminal, navigate to your backend folder, and activate the virtual environment as shown in Part 1, Step 3.



Run the Server:

Use the command for your operating system to start the Flask server.



For Windows:

.\\venv\\Scripts\\python.exe app.py



For macOS/Linux:

./venv/bin/python app.py



The server is now running at http://127.0.0.1:5001 (local)



**Part 3: Running the Unit Tests with Pytest**

Open Terminal and Activate Environment:

If it's not already active, a new terminal in your backend folder and activate the virtual environment.



Run Pytest:

To run all the tests in your test\_app.py file, simply run the following command:



pytest



Pytest will automatically discover and run all the tests for you. You will see the results (passes and failures) in the terminal.



**Part 4: Generating a Code Coverage Report**

Activate Environment:

Ensure your virtual environment is active in your terminal.



Generate a Terminal Report:

To see a quick summary of your test coverage in the terminal, run:



pytest --cov=app



Generate a Detailed HTML Report (Recommended):

For a more detailed, line-by-line report, run the following command:



pytest --cov=app --cov-report=html



This will create a new folder named htmlcov in your project directory. Open the index.html file inside that folder in your web browser to see the interactive report.

***TO EXIT VIRUAL ENVIRONMENT: run the command: deactivate to quit***

