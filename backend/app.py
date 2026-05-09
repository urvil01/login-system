from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import random
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
CORS(app)

# EMAIL CONFIG
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")


# CREATE DATABASE
def init_db():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute('''

        CREATE TABLE IF NOT EXISTS users(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE,

            password TEXT,

            otp TEXT,

            verified INTEGER DEFAULT 0

        )

    ''')

    conn.commit()
    conn.close()


init_db()


# SEND OTP
def send_otp(receiver_email, otp):

    try:

        msg = EmailMessage()

        msg["Subject"] = "OTP Verification"

        msg["From"] = SENDER_EMAIL

        msg["To"] = receiver_email

        msg.set_content(f"Your OTP is: {otp}")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

        server.login(SENDER_EMAIL, APP_PASSWORD)

        server.send_message(msg)

        server.quit()

        print("OTP SENT SUCCESSFULLY")

        return True

    except Exception as e:

        print("EMAIL ERROR:", e)

        return False


# LOGIN API
@app.route('/login', methods=['POST'])
def login():

    data = request.json

    email = data['email']
    password = data['password']
    signup = data['signup']

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    # CHECK USER
    cur.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cur.fetchone()

    # SIGNUP
    if signup:

        if user:

            conn.close()

            return jsonify({
                "success": False,
                "message": "Account already exists"
            })

        otp = str(random.randint(100000,999999))

        cur.execute(
            "INSERT INTO users(email,password,otp) VALUES(?,?,?)",
            (email,password,otp)
        )

        conn.commit()

        # SEND OTP
        email_sent = send_otp(email, otp)

        conn.close()

        if email_sent:

            return jsonify({
                "success": True,
                "verified": False
            })

        else:

            return jsonify({
                "success": False,
                "message": "Email not sent"
            })

    # SIGNIN
    else:

        if not user:

            conn.close()

            return jsonify({
                "success": False,
                "message": "Account not found"
            })

        db_password = user[2]
        verified = user[4]

        if password != db_password:

            conn.close()

            return jsonify({
                "success": False,
                "message": "Wrong password"
            })

        # VERIFIED USER
        if verified == 1:

            conn.close()

            return jsonify({
                "success": True,
                "verified": True
            })

        # NOT VERIFIED
        otp = str(random.randint(100000,999999))

        cur.execute(
            "UPDATE users SET otp=? WHERE email=?",
            (otp,email)
        )

        conn.commit()

        email_sent = send_otp(email, otp)

        conn.close()

        if email_sent:

            return jsonify({
                "success": True,
                "verified": False
            })

        else:

            return jsonify({
                "success": False,
                "message": "Email not sent"
            })


# VERIFY API
@app.route('/verify', methods=['POST'])
def verify():

    data = request.json

    email = data['email']
    otp = data['otp']

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    # CHECK OTP
    cur.execute(
        "SELECT * FROM users WHERE email=? AND otp=?",
        (email, otp)
    )

    user = cur.fetchone()

    # OTP CORRECT
    if user:

        cur.execute(
            "UPDATE users SET verified=1, otp='' WHERE email=?",
            (email,)
        )

        conn.commit()

        conn.close()

        return jsonify({
            "success": True,
            "message": "OTP Verified"
        })

    # WRONG OTP
    conn.close()

    return jsonify({
        "success": False,
        "message": "Invalid OTP"
    })
@app.route('/users')
def users():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM users")

    data = cur.fetchall()

    conn.close()

    return jsonify(data)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
