import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import random
import string
from datetime import datetime, timedelta
import jwt
import hashlib
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Initialize the Flask application
app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['AGORA_APP_ID'] = os.environ.get('AGORA_APP_ID')
app.config['AGORA_APP_CERTIFICATE'] = os.environ.get('AGORA_APP_CERTIFICATE')

# Ensure that the DATABASE_URL is properly defined
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise ValueError("No DATABASE_URL found in environment variables.")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
mail = Mail(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    uses = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    report_type = db.Column(db.Enum('Medical', 'Behavioral', 'Other'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('Pending', 'In Progress', 'Resolved'), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VideoCall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('Scheduled', 'Completed', 'Cancelled'), default='Scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MedicineRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id', ondelete='CASCADE'))
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete='CASCADE'))
    dosage = db.Column(db.Text)
    recommendation = db.Column(db.Text)


# Agora configuration
AGORA_APP_ID = app.config['AGORA_APP_ID']
AGORA_APP_CERTIFICATE = app.config['AGORA_APP_CERTIFICATE']

def generate_agora_token(channel_name, uid):
    current_time = datetime.utcnow()
    expiration_time = current_time + timedelta(hours=1)
    token_expiration = int(expiration_time.timestamp())

    sign_key = hashlib.sha256(f"{AGORA_APP_ID}{AGORA_APP_CERTIFICATE}{current_time}".encode()).hexdigest()
    token_data = {
        "app_id": AGORA_APP_ID,
        "uid": uid,
        "channel_name": channel_name,
        "iat": int(current_time.timestamp()),
        "exp": token_expiration,
        "sign_key": sign_key
    }

    token = jwt.encode(token_data, AGORA_APP_CERTIFICATE, algorithm='HS256')
    return token


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        if request.content_type != 'application/json':
            return jsonify({'success': False, 'message': 'Unsupported Media Type'}), 415

        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return jsonify({'success': True})

        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        if request.content_type != 'application/json':
            return jsonify({'success': False, 'message': 'Unsupported Media Type'}), 415

        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')

        # Log the received data
        print(f"Received data for registration: {data}")

        if Users.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400

        hashed_password = generate_password_hash(password)
        new_user = Users(username=username, email=email, password_hash=hashed_password, phone_number=phone)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True})


@app.route('/forget_password')
def forget_password():
    return render_template('forget_password.html')


@app.route('/hospitals')
def hospitals():
    return render_template('hospitals.html')


@app.route('/video_call')
def video_call():
    return render_template('video_call.html')


@app.route('/report')
def report():
    return render_template('report.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/medicine')
def medicine():
    return render_template('medicine.html')


@app.route('/request_otp', methods=['POST'])
def request_otp():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Unsupported Media Type'}), 415

    data = request.json
    email = data.get('email')

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    otp_code = ''.join(random.choices(string.digits, k=6))
    session['otp_code'] = otp_code
    session['user_id'] = user.id

    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP Code is {otp_code}'
    mail.send(msg)

    return jsonify({'success': True, 'otpCode': otp_code})


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Unsupported Media Type'}), 415

    data = request.json
    otp = data.get('otp')

    if otp == session.get('otp_code'):
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid OTP'}), 400


@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Unsupported Media Type'}), 415

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Session expired'}), 400

    user = Users.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    otp_code = ''.join(random.choices(string.digits, k=6))
    session['otp_code'] = otp_code

    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f'Your OTP Code is {otp_code}'
    mail.send(msg)

    return jsonify({'success': True, 'otpCode': otp_code})


@app.route('/get_hospitals', methods=['GET'])
def get_hospitals():
    hospitals = Hospital.query.all()
    hospital_data = [
        {
            'id': hospital.id,
            'name': hospital.name,
            'address': hospital.address,
            'phone_number': hospital.phone_number,
            'email': hospital.email,
            'latitude': hospital.latitude,
            'longitude': hospital.longitude
        } for hospital in hospitals
    ]
    return jsonify(hospital_data)


@app.route('/get_medicines', methods=['GET'])
def get_medicines():
    medicines = Medicine.query.all()
    medicine_data = [
        {
            'id': medicine.id,
            'name': medicine.name,
            'description': medicine.description,
            'uses': medicine.uses,
            'side_effects': medicine.side_effects
        } for medicine in medicines
    ]
    return jsonify(medicine_data)


@app.route('/get_reports', methods=['GET'])
def get_reports():
    reports = Report.query.all()
    report_data = [
        {
            'id': report.id,
            'user_id': report.user_id,
            'report_type': report.report_type,
            'description': report.description,
            'status': report.status,
            'created_at': report.created_at,
            'updated_at': report.updated_at
        } for report in reports
    ]
    return jsonify(report_data)


@app.route('/get_video_call_token', methods=['POST'])
def get_video_call_token():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Unsupported Media Type'}), 415

    data = request.json
    channel_name = data.get('channelName')
    uid = data.get('uid', random.randint(10000, 99999))

    token = generate_agora_token(channel_name, uid)
    return jsonify({'success': True, 'token': token})


#chatbot app.py

import google.generativeai as genai
import json
import re

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-latest")
chat = model.start_chat(history=[])

conversation_file = 'conversations.json'

def load_conversations():
    if os.path.exists(conversation_file):
        with open(conversation_file, 'r') as f:
            return json.load(f)
    return {}

def save_conversation(user_input, response):
    conversations = load_conversations()
    conversations[user_input] = response
    with open(conversation_file, 'w') as f:
        json.dump(conversations, f, indent=4)

def get_gemini_response(user_input):
    response = chat.send_message(user_input, stream=True)
    full_response = ""
    for chunk in response:
        full_response += chunk.text
    save_conversation(user_input, full_response)
    return full_response

@app.route('/HosBot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json.get('message')
    conversations = load_conversations()

    if user_input in conversations:
        response = conversations[user_input]
    else:
        response = get_gemini_response(user_input)
        response = re.sub(r"\*", "", response)
    
    return jsonify({'response': response})



if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"An error occurred while creating the database tables: {e}")
    app.run(debug=True)


