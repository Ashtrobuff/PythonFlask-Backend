from flask import *  
from flask_mail import *  
import random
import datetime
import jwt
from models import User
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, email, otp):
        self.email = email
        self.otp = otp

    def is_otp_valid(self, otp):
        expiration_time = self.created_at + timedelta(minutes=5)
        if datetime.utcnow() > expiration_time:
            return False
        return self.otp == otp
 
app.config['MAIL_SERVER']='smtp.gmail.com'  
app.config['MAIL_PORT']=465  
app.config['MAIL_USERNAME'] = 'sheeeshnator4000@gmail.com'  
app.config['MAIL_PASSWORD'] = 'umhz pzgm egzk nbrr'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  

SECRET_KEY = 'shashiburida123k2rk'
otp_storage = {}
mail = Mail(app)  
def generate_otp():
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    return otp

def verify_otp(email, otp):
    otp_entry = OTP.query.filter_by(email=email).first()
    if otp_entry and otp_entry.is_otp_valid(otp):
        return True
    else:
        return False
    

#configure the Message class object and send the mail from a URL  
@app.route('/register')  
def index():  
    data=request.json
    mail1=data.get('email')
    existing_user = User.query.filter_by(email=mail1).first()
    if existing_user:
        return jsonify({"message": "User already exists."}), 400

    new_user = User(email=mail1)
    db.session.add(new_user)
    db.session.commit()
    with mail.connect() as con:
        msg = Message('subject', sender = 'sheeeshnator4000@gmail.com', recipients=[mail1])  
        msg.body = 'hi, this is the mail sent by using the flask web application'  
        con.send(msg)
    return "Mail Sent, Please check the mail id"  


@app.route('/request-otp')  
def sendOtp():  
    data=request.json
    mail1=data.get('email')
    otp = generate_otp()
    otp_entry = OTP.query.filter_by(email=mail1).first()
    if otp_entry:
        otp_entry.otp = otp
        otp_entry.created_at = datetime.utcnow()
    else:
        otp_entry = OTP(email=mail1, otp=otp)
        db.session.add(otp_entry)
    db.session.commit()
    with mail.connect() as con:
        msg = Message('subject', sender = 'sheeeshnator4000@gmail.com', recipients=[mail1])  
        msg.body = 'This is the OTP for verification'+str(otp)  
        con.send(msg)
    
    return "Mail Sent, Please check the mail id"  

@app.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({"message": "Email and OTP are required."}), 400

    if verify_otp(email, otp):
        # Generate a JWT token (for demonstration purposes)
        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            "message": "Login successful.",
            "token": token
        }), 200
    else:
        return jsonify({"message": "Invalid OTP."}), 400

@app.route('/api/users', methods=['GET'])
def get_users():
    users = session.query(User).all()
    users_list = [
        {"id": user.id, "email": user.email}
        for user in users
    ]
    return jsonify(users_list)
if __name__ == '__main__':  
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug = True)  