from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, User, Query, Meet, Message
import hashlib
import secrets

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///peerlift.db"
db.init_app(app)

with app.app_context():
    db.create_all()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    return secrets.token_hex(32) + str(user_id)

# ==========================================
# AUTH
# ==========================================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"error": "All fields required"}), 400
    existing = User.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409
    user = User(
        name=data["name"],
        email=data["email"],
        password=hash_password(data["password"]),
        token=generate_token(0)
    )
    db.session.add(user)
    db.session.commit()
    user.token = generate_token(user.id)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name, "email": user.email, "token": user.token}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(
        email=data["email"],
        password=hash_password(data["password"])
    ).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    return jsonify({"id": user.id, "name": user.name, "email": user.email, "token": user.token}), 200

# ==========================================
# USERS
# ==========================================
@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

# ==========================================
# QUERIES
# ==========================================
@app.route("/api/queries", methods=["GET"])
def get_queries():
    queries = Query.query.order_by(Query.id.desc()).all()
    return jsonify([{
        "id": q.id, "title": q.title,
        "description": q.description,
        "subject": q.subject,
        "author": q.author,
        "target": q.target
    } for q in queries])

@app.route("/api/queries", methods=["POST"])
def post_query():
    data = request.json
    q = Query(
        title=data["title"],
        description=data["description"],
        subject=data.get("subject", "General"),
        author=data.get("author", "Anonymous"),
        target=data.get("target", "")
    )
    db.session.add(q)
    db.session.commit()
    return jsonify({"message": "Query posted", "id": q.id}), 201

# ==========================================
# MEETS
# ==========================================
@app.route("/api/meets", methods=["GET"])
def get_meets():
    meets = Meet.query.order_by(Meet.id.desc()).all()
    return jsonify([{
        "id": m.id, "subject": m.subject,
        "topic": m.topic, "date": m.date,
        "time": m.time, "host": m.host,
        "description": m.description
    } for m in meets])

@app.route("/api/meets", methods=["POST"])
def schedule_meet():
    data = request.json
    m = Meet(
        subject=data.get("subject", ""),
        topic=data["topic"],
        description=data.get("description", ""),
        date=data["date"],
        time=data["time"],
        host=data.get("host", "Anonymous")
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"message": "Meet scheduled", "id": m.id}), 201

# ==========================================
# MESSAGES
# ==========================================
@app.route("/api/messages", methods=["GET"])
def get_messages():
    user1 = request.args.get("user1")
    user2 = request.args.get("user2")
    messages = Message.query.filter(
        ((Message.sender == user1) & (Message.receiver == user2)) |
        ((Message.sender == user2) & (Message.receiver == user1))
    ).order_by(Message.id.asc()).all()
    return jsonify([{
        "id": m.id,
        "sender": m.sender,
        "receiver": m.receiver,
        "message": m.message
    } for m in messages])

@app.route("/api/messages", methods=["POST"])
def send_message():
    data = request.json
    m = Message(
        sender=data["sender"],
        receiver=data["receiver"],
        message=data["message"]
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"message": "Sent", "id": m.id}), 201

if __name__ == "__main__":
    app.run(debug=True)