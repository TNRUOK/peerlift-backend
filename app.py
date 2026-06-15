from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, User, Query, Meet

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///peerlift.db"
db.init_app(app)

with app.app_context():
    db.create_all()

# --- USER ---
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(name=data["name"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name}), 201

# --- QUERIES ---
@app.route("/api/queries", methods=["GET"])
def get_queries():
    queries = Query.query.all()
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
        subject=data.get("subject", ""),
        author=data.get("author", "Anonymous"),
        target=data.get("target", "")
    )
    db.session.add(q)
    db.session.commit()
    return jsonify({"message": "Query posted", "id": q.id}), 201

# --- MEETS ---
@app.route("/api/meets", methods=["GET"])
def get_meets():
    meets = Meet.query.all()
    return jsonify([{
        "id": m.id, "subject": m.subject,
        "topic": m.topic, "date": m.date,
        "time": m.time, "host": m.host
    } for m in meets])

@app.route("/api/meets", methods=["POST"])
def schedule_meet():
    data = request.json
    m = Meet(
        subject=data["subject"],
        topic=data["topic"],
        description=data.get("description", ""),
        date=data["date"],
        time=data["time"],
        host=data.get("host", "Anonymous")
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"message": "Meet scheduled", "id": m.id}), 201

if __name__ == "__main__":
    app.run(debug=True)