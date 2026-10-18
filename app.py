from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devsync.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Snippet(db.Model):
    __tablename__ = 'snippets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    code_content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default='python')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "code_content": self.code_content,
            "language": self.language,
            "created_at": self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({"error": "Missing required fields"}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 400

    hashed_password = generate_password_hash(data['password'])
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password
    )
    
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": user.id}), 201

@app.route('/api/snippets', methods=['GET'])
def get_snippets():
    snippets = Snippet.query.all()
    return jsonify([s.to_dict() for s in snippets]), 200

@app.route('/api/snippets', methods=['POST'])
def create_snippet():
    data = request.get_json()

    if not data or not data.get('title') or not data.get('code_content'):
        return jsonify({"error": "Title and code content are required"}), 400

    snippet = Snippet(
        title=data['title'],
        code_content=data['code_content'],
        language=data.get('language', 'python')
    )
    
    db.session.add(snippet)
    db.session.commit()

    return jsonify({"message": "Snippet created", "snippet": snippet.to_dict()}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)