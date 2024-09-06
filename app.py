import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Ensure that the DATABASE_URL is properly defined
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise ValueError("No DATABASE_URL found in environment variables.")

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Database model for Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.username}>"

# Function to create the database tables
def create_db():
    with app.app_context():
        db.create_all()

# Route for displaying homepage and handling form submission for creating users
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_hash = generate_password_hash(request.form['password'])
        full_name = request.form.get('full_name', '')
        phone_number = request.form.get('phone_number', '')
        address = request.form.get('address', '')

        user = Users(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone_number=phone_number,
            address=address,
        )
        db.session.add(user)
        db.session.commit()

    all_users = Users.query.all()
    return render_template('index.html', allUsers=all_users)

# Route for updating user information
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user = Users.query.get_or_404(id)  # Simplified retrieval with error handling

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.password_hash = generate_password_hash(request.form['password'])
        user.full_name = request.form.get('full_name', user.full_name)
        user.phone_number = request.form.get('phone_number', user.phone_number)
        user.address = request.form.get('address', user.address)

        db.session.commit()
        return redirect('/')  # Use url_for for better practice
        
    return render_template('update.html', user=user)

# Route for deleting a user
@app.route('/delete/<int:id>')
def delete_user(id):
    user = Users.query.get_or_404(id)  # Simplified retrieval with error handling
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

# Route for displaying login page and handling login requests
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

# Route for handling registration
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
    create_db()  # Call the function to create the database tables
    app.run(debug=True)

