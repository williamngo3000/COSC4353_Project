from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from models import (
    db, UserCredentials, UserProfile, EventDetails,
    Invite, VolunteerHistory, Notification, ActivityLog
)
import os
from datetime import datetime, date

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # Allow React frontend to call Flask


#  Database configuration — create & bind immediately
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'volunteer.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  #  directly bind db to app here

def parse_date_str(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def event_current_volunteers(event_id: int) -> int:
    return Invite.query.filter_by(event_id=event_id, status="accepted").count()

def check_and_close_event(event: EventDetails) -> bool:
    if event.status == "closed":
        return False
    today = datetime.now().date()
    if event.event_date < today:
        event.status = "closed"
        db.session.commit()
        return True
    if event.volunteer_limit is not None:
        if event_current_volunteers(event.id) >= event.volunteer_limit:
            event.status = "closed"
            db.session.commit()
            return True
    return False

def add_notification(message: str, type: str = "info"):
    n = Notification(message=message, type=type, time=datetime.utcnow())
    db.session.add(n)
    db.session.commit()
    return n

def add_activity(kind: str, **kwargs):
    a = ActivityLog(type=kind, time=datetime.utcnow(), meta=kwargs or None)
    db.session.add(a)
    db.session.commit()
    return a


@app.route("/register", methods=["POST"])
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

@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = UserCredentials.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    profile = UserProfile.query.get(user.id)
    return jsonify({
        "message": "Login successful",
        "user": {
            "email": user.email,
            "role": user.role,
            "profileComplete": bool(profile is not None)
        }
    }), 200

@app.route("/profile/<string:email>", methods=["GET", "PUT"])
def user_profile(email):
    user = UserCredentials.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if request.method == "GET":
        p = UserProfile.query.get(user.id)
        if not p:
            return jsonify({}), 200
        return jsonify({
            "full_name": p.full_name,
            "address1": p.address1,
            "address2": p.address2,
            "city": p.city,
            "state": p.state,
            "zip_code": p.zip_code,
            "phone": p.phone,
            "skills": p.skills or [],
            "preferences": p.preferences or "",
            "availability": p.availability or []
        }), 200

    data = request.get_json() or {}
    p = UserProfile.query.get(user.id)
    if not p:
        p = UserProfile(id=user.id)
        db.session.add(p)

    p.full_name = data.get("full_name", "")
    p.address1 = data.get("address1", "")
    p.address2 = data.get("address2")
    p.city = data.get("city", "")
    p.state = data.get("state", "")
    p.zip_code = data.get("zip_code", "")
    p.phone = data.get("phone")
    p.skills = data.get("skills", [])
    p.preferences = data.get("preferences")
    p.availability = data.get("availability", [])

    db.session.commit()
    return jsonify({"message": "Profile updated successfully", "profile": request.get_json() or {}}), 200

@app.route("/events", methods=["GET", "POST"])
def events():
    if request.method == "GET":
        for ev in EventDetails.query.filter_by(status="open").all():
            check_and_close_event(ev)

        out = []
        for ev in EventDetails.query.all():
            out.append({
                "id": ev.id,
                "event_name": ev.event_name,
                "description": ev.description,
                "location": ev.location,
                "required_skills": ev.required_skills or [],
                "urgency": ev.urgency,
                "event_date": ev.event_date.strftime("%Y-%m-%d"),
                "volunteer_limit": ev.volunteer_limit,
                "status": ev.status,
                "current_volunteers": event_current_volunteers(ev.id)
            })
        return jsonify(out), 200

    data = request.get_json() or {}
    ev = EventDetails(
        event_name=data["event_name"],
        description=data["description"],
        location=data["location"],
        required_skills=data.get("required_skills", []),
        urgency=data["urgency"],
        event_date=parse_date_str(data["event_date"]),
        volunteer_limit=data.get("volunteer_limit"),
        status="open",
    )
    db.session.add(ev)
    db.session.commit()

    add_notification(f"New event created: {ev.event_name}", "success")
    add_activity("event_created", event=ev.event_name)

    return jsonify({"message": "Event created successfully", "event": {
        "id": ev.id,
        "event_name": ev.event_name,
        "description": ev.description,
        "location": ev.location,
        "required_skills": ev.required_skills or [],
        "urgency": ev.urgency,
        "event_date": ev.event_date.strftime("%Y-%m-%d"),
        "volunteer_limit": ev.volunteer_limit,
        "status": ev.status
    }}), 201

@app.route("/matching/<int:event_id>", methods=["GET"])
def get_matches(event_id):
    ev = EventDetails.query.get(event_id)
    if not ev:
        return jsonify({"message": "Event not found"}), 404

    matches = []
    users = UserCredentials.query.filter_by(role="volunteer").all()
    for u in users:
        p = UserProfile.query.get(u.id)
        if not p:
            continue
        has_skill = any(s in (p.skills or []) for s in (ev.required_skills or []))
        is_available = ev.event_date.strftime("%Y-%m-%d") in (p.availability or [])
        if has_skill and is_available:
            matches.append({
                "email": u.email,
                "full_name": p.full_name,
                "skills": p.skills or []
            })
    return jsonify(matches), 200

@app.route("/invites", methods=["GET", "POST"])
def invites():
    if request.method == "GET":
        status = request.args.get("status")
        inv_type = request.args.get("type")
        q = Invite.query
        if status: q = q.filter_by(status=status)
        if inv_type: q = q.filter_by(type=inv_type)
        res = []
        for inv in q.order_by(Invite.created_at.desc()).all():
            res.append({
                "id": inv.id,
                "event_id": inv.event_id,
                "user_email": inv.user_email,
                "status": inv.status,
                "type": inv.type,
                "created_at": inv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "completed": inv.completed
            })
        return jsonify(res), 200

    data = request.get_json() or {}
    ev = EventDetails.query.get(data["event_id"])
    if not ev:
        return jsonify({"message": "Event not found"}), 404

    check_and_close_event(ev)
    if ev.status == "closed":
        return jsonify({"message": "This event is now closed and no longer accepting volunteers"}), 403

    exists = Invite.query.filter(
        Invite.event_id == data["event_id"],
        Invite.user_email == data["user_email"],
        Invite.status.in_(["pending", "accepted"])
    ).first()
    if exists:
        if exists.status == "pending":
            return jsonify({"message": "You already have a pending request for this event"}), 409
        return jsonify({"message": "You are already signed up for this event"}), 409

    inv = Invite(
        event_id=data["event_id"],
        user_email=data["user_email"],
        status="pending",
        type=data["type"]
    )
    db.session.add(inv)
    db.session.commit()

    event_name = ev.event_name
    if inv.type == "admin_invite":
        add_notification(f"You've been invited to: {event_name}", "info")
    elif inv.type == "user_request":
        add_notification(f"{inv.user_email} requested to join: {event_name}", "info")

    return jsonify({"message": "Invite/request created successfully", "invite": {
        "id": inv.id,
        "event_id": inv.event_id,
        "user_email": inv.user_email,
        "status": inv.status,
        "type": inv.type,
        "created_at": inv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "completed": inv.completed
    }}), 201


@app.route("/invites/<int:invite_id>", methods=["PUT", "DELETE"])
def invite_by_id(invite_id):
    inv = Invite.query.get(invite_id)
    if not inv:
        return jsonify({"message": "Invite not found"}), 404

    if request.method == "PUT":
        data = request.get_json() or {}
        old_status = inv.status
        inv.status = data.get("status", inv.status)
        db.session.commit()

        if old_status != "accepted" and inv.status == "accepted":
            ev = EventDetails.query.get(inv.event_id)
            if ev: check_and_close_event(ev)

        return jsonify({"message": "Invite updated successfully", "invite": {
            "id": inv.id, "event_id": inv.event_id, "user_email": inv.user_email,
            "status": inv.status, "type": inv.type,
            "created_at": inv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed": inv.completed
        }}), 200

    db.session.delete(inv)
    db.session.commit()
    return jsonify({"message": "Invite deleted successfully"}), 200


@app.route("/invites/<int:invite_id>/complete", methods=["PUT"])
def invite_complete(invite_id):
    inv = Invite.query.get(invite_id)
    if not inv:
        return jsonify({"message": "Invite not found"}), 404

    data = request.get_json() or {}
    completed = bool(data.get("completed", False))
    inv.completed = completed
    db.session.commit()

    if inv.status == "accepted":
        if completed:
            exists = VolunteerHistory.query.filter_by(
                user_email=inv.user_email, event_id=inv.event_id
            ).first()
            if not exists:
                vh = VolunteerHistory(user_email=inv.user_email, event_id=inv.event_id)
                db.session.add(vh)
                db.session.commit()
        else:
            exists = VolunteerHistory.query.filter_by(
                user_email=inv.user_email, event_id=inv.event_id
            ).first()
            if exists:
                db.session.delete(exists)
                db.session.commit()

    return jsonify({"message": "Completion status updated successfully", "invite": {
        "id": inv.id, "event_id": inv.event_id, "user_email": inv.user_email,
        "status": inv.status, "type": inv.type,
        "created_at": inv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "completed": inv.completed
    }}), 200


@app.route("/user/<string:email>/events", methods=["GET"])
def user_events(email):
    accepted = Invite.query.filter_by(user_email=email, status="accepted").all()
    events = []
    for inv in accepted:
        ev = EventDetails.query.get(inv.event_id)
        if ev:
            events.append({
                "id": ev.id,
                "event_name": ev.event_name,
                "description": ev.description,
                "location": ev.location,
                "event_date": ev.event_date.strftime("%Y-%m-%d"),
                "required_skills": ev.required_skills or [],
                "urgency": ev.urgency,
                "completed": inv.completed
            })
    return jsonify({"events": events}), 200

@app.route("/users", methods=["GET"])
def all_users():
    rows = []
    for u in UserCredentials.query.all():
        p = UserProfile.query.get(u.id)
        rows.append({
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "name": p.full_name if p else "N/A",
            "phone": p.phone if p else "N/A",
            "profileComplete": bool(p)
        })
    return jsonify(rows), 200

@app.route("/notifications", methods=["GET"])
def notifications():
    out = []
    for n in Notification.query.order_by(Notification.time.desc()).limit(50).all():
        out.append({
            "id": n.id,
            "message": n.message,
            "type": n.type,
            "time": n.time.strftime("%Y-%m-%d %H:%M:%S"),
            "read": getattr(n, "read", False)  # read, maybe add later
        })
    return jsonify(out), 200

@app.route("/notifications/<int:notification_id>/read", methods=["PUT"])
def mark_notification_read(notification_id):
    n = Notification.query.get(notification_id)
    if not n:
        return jsonify({"message": "Notification not found"}), 404

    return jsonify({"message": "Notification marked as read"}), 200

@app.route("/activity", methods=["GET"])
def activity():
    out = []
    for a in ActivityLog.query.order_by(ActivityLog.time.desc()).limit(50).all():
        out.append({
            "type": a.type,
            "time": a.time.strftime("%Y-%m-%d %H:%M:%S"),
            **(a.meta or {})
        })
    return jsonify(out), 200

@app.route("/data/skills", methods=["GET"])
def data_skills():
    return jsonify(["First Aid","Logistics","Event Setup","Public Speaking","Registration",
                    "Tech Support","Catering","Marketing","Fundraising","Photography",
                    "Social Media","Team Leadership","Translation"]), 200

@app.route("/data/urgency", methods=["GET"])
def data_urgency():
    return jsonify(["Low","Medium","High","Critical"]), 200

@app.route("/events/<int:event_id>", methods=["GET", "PUT", "DELETE"])
def event_by_id(event_id):
    ev = EventDetails.query.get(event_id)
    if not ev:
        return jsonify({"message": "Event not found"}), 404

    if request.method == "GET":
        return jsonify({
            "id": ev.id,
            "event_name": ev.event_name,
            "description": ev.description,
            "location": ev.location,
            "required_skills": ev.required_skills or [],
            "urgency": ev.urgency,
            "event_date": ev.event_date.strftime("%Y-%m-%d"),
            "volunteer_limit": ev.volunteer_limit,
            "status": ev.status
        }), 200

    if request.method == "PUT":
        data = request.get_json() or {}
        ev.event_name = data["event_name"]
        ev.description = data["description"]
        ev.location = data["location"]
        ev.required_skills = data.get("required_skills", [])
        ev.urgency = data["urgency"]
        ev.event_date = parse_date_str(data["event_date"])
        ev.volunteer_limit = data.get("volunteer_limit")
        db.session.commit()
        return jsonify({"message": "Event updated successfully", "event": {
            "id": ev.id,
            "event_name": ev.event_name,
            "description": ev.description,
            "location": ev.location,
            "required_skills": ev.required_skills or [],
            "urgency": ev.urgency,
            "event_date": ev.event_date.strftime("%Y-%m-%d"),
            "volunteer_limit": ev.volunteer_limit,
            "status": ev.status
        }}), 200

    db.session.delete(ev)
    db.session.commit()
    return jsonify({"message": "Event deleted successfully"}), 200


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

    app.run(debug=True, port=5001)
