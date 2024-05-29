from flask import Flask, session, abort, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

app = Flask(__name__)
CORS(app)
app.secret_key = "YourSecretKeyHere"  # Thay bằng một khóa bí mật thực tế
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%40nts28PtMySQL@localhost/localog_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(100), nullable=True)

class CheckPlace(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    description = Column(String(100))
    radius = Column(Integer)
    typeMap = Column(String(100))
    longitude = Column(Float)
    latitude = Column(Float)
    is_active = Column(Boolean, default=True)

# class HistoryChecked(db.Model):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     checkPlace_id = Column(Integer, ForeignKey('checkPlace.id'))
#     timeChecked = Column(Date)
#     user = relationship("User", backref="history_checked")
#     check_place = relationship("CheckPlace", backref="history_checked")


@app.route('/')
def home():
    return jsonify({"message": "Welcome"})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if email is None or password is None:
        return jsonify({"message": "Missing email or password"}), 400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"message": "Email already exists"}), 400

    user = User(email=email, password=password, name=name)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(data)
    user = User.query.filter_by(email=email, password=password).first()

    if user is None:
        return jsonify({"message": "Invalid email or password"}), 401
    
    print(user)

    user_data = {
        "email": user.email,
        "name": user.name
    }

    session['email'] = email
    return jsonify({"message": "Login successful", "user_data": user_data}), 200

@app.route('/protect')
def protect():
    if 'email' not in session:
        abort(401)
    return jsonify({"message": f"Hello {session['email']}!"})

@app.route('/checkPlace')
def checkPlace():

    return 0


@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
