from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from models import db, UserCredentials  # import db from models
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # Allow React frontend to call Flask


#  Database configuration — create & bind immediately
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'volunteer.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  #  directly bind db to app here


@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if UserCredentials.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = UserCredentials(
        email=email,
        password_hash=generate_password_hash(password),
        role="admin" if email == "admin@example.com" else "volunteer"
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@app.route("/api/test")
def test():
    return {"message": "Flask is running!"}

@app.route("/api/session")
def get_session():
    email = request.args.get("email")
    user = UserCredentials.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email,
        "role": user.role
    }), 200


if __name__ == "__main__":
    # Always run db.create_all() inside app context
    with app.app_context():
        db.create_all()
        print("Database initialized at:", os.path.abspath("volunteer.db"))

    app.run(debug=True, port=5002)

