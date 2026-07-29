# pyright: reportMissingImports=false
from abc import ABC, abstractmethod
from flask import ( 
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
import flask

from werkzeug.security import generate_password_hash, check_password_hash

import traceback
import json
import os

import automation as automation_module

from database import Database
from voice import VoiceAssistant
from ai import AIAssistant
from automation import AutomationManager
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


app = Flask(__name__)
print("Template folder:", app.template_folder)
print("Root path:", app.root_path)
app.secret_key = "your-secret-key-here"

# ===========================
# Gmail Configuration
# ===========================

EMAIL_ADDRESS = "singh123sneha45@gmail.com"
EMAIL_PASSWORD = "xqne vgnh dpwx bhhp" # Use App Password if 2FA is enabled

import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()   # Print full error in terminal
    return f"""
    <h2>Python Error</h2>
    <pre>{traceback.format_exc()}</pre>
    """, 500

db = Database()
voice_assistant = VoiceAssistant()
ai_assistant = AIAssistant()
automation_manager = AutomationManager()

def send_otp(email, otp):

    subject = "Smart Home AI - Password Reset OTP"

    body = f"""
<html>

<head>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f4f4f4;
    padding: 20px;
}}

.container {{
    max-width: 600px;
    margin: auto;
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
}}

.header {{
    background: #007BFF;
    color: white;
    text-align: center;
    padding: 20px;
}}

.content {{
    padding: 30px;
}}

.otp {{
    font-size: 32px;
    font-weight: bold;
    text-align: center;
    color: #007BFF;
    letter-spacing: 8px;
    margin: 25px 0;
}}

.note {{
    background: #f8f9fa;
    border-left: 5px solid #007BFF;
    padding: 15px;
    margin-top: 20px;
}}

.footer {{
    background: #f4f4f4;
    text-align: center;
    padding: 15px;
    color: gray;
    font-size: 13px;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>🏠 Smart Home AI</h1>

<p>Password Reset Verification</p>

</div>

<div class="content">

<h2>Hello!</h2>

<p>
We received a request to reset the password for your
<b>Smart Home AI</b> account.
</p>

<p>
Use the verification code below:
</p>

<div class="otp">
{otp}
</div>

<div class="note">

<b>Important</b>

<ul>

<li>This OTP is valid for only <b>1 minute</b>.</li>

<li>Do not share this code with anyone.</li>

<li>If you didn't request this password reset, simply ignore this email.</li>

</ul>

</div>

<p>

Thank you,<br>

<b>Smart Home AI Team</b>

</p>

</div>

<div class="footer">

© 2026 Smart Home AI

</div>

</div>

</body>

</html>
"""
    message = MIMEMultipart()
    message["From"] = f"Smart Home AI <{EMAIL_ADDRESS}>"
    message["To"] = email
    message["Subject"] = subject
    message["Reply-To"] = EMAIL_ADDRESS

    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        server.sendmail(
            EMAIL_ADDRESS,
            email,
            message.as_string()
        )
        print("OTP EMAIL SENT TO:", email)
        server.quit()

        return True

    except Exception as e:
        print("Email Error:", e)
        return False

@app.route("/")
def index():
    devices = db.get_devices()
    return flask.render_template("index.html", devices=devices)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    devices = db.get_devices()
    return flask.jsonify({'status': 'success', 'devices': devices})

@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get specific device details"""
    device = db.get_device(device_id)
    if device:
        return flask.jsonify({'status': 'success', 'device': device})
    return flask.jsonify({'status': 'error', 'message': 'Device not found'}), 404

@app.route('/api/devices', methods=['POST'])
def add_device():
    """Add new device"""
    data = flask.request.json
    device_id = db.add_device(
        name=data['name'],
        type=data['type'],
        room=data.get('room', 'Living Room'),
        status='off'
    )
    return flask.jsonify({'status': 'success', 'device_id': device_id})

@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device status"""
    data = flask.request.json
    status = data.get('status')
    if status in ['on', 'off']:
        db.update_status(device_id, status)
        automation_manager.check_rules()
        return flask.jsonify({'status': 'success'})
    return flask.jsonify({'status': 'error', 'message': 'Invalid status'}), 400

@app.route('/api/voice/command', methods=['POST'])
def voice_command():
    """Process voice command"""
    data = flask.request.json
    command = data.get('command')
    
    # Convert speech to text if audio is provided
    if data.get('audio'):
        command = voice_assistant.speech_to_text(data['audio'])
    
    # Process command with AI
    result = ai_assistant.process_command(command)
    
    # Execute automation if needed
    if result.get('action'):
        automation_manager.execute_action(result['action'])
    
    # Convert response to speech if requested
    if data.get('speak_response'):
        voice_assistant.text_to_speech(result['response'])
    
    return flask.jsonify(result)

@app.route('/api/automation/rules', methods=['GET'])
def get_rules():
    """Get all automation rules"""
    rules = db.get_all_rules()
    return flask.jsonify({'status': 'success', 'rules': rules})

@app.route('/api/automation/rules', methods=['POST'])
def add_rule():
    """Add new automation rule"""
    data = flask.request.json
    rule_id = db.add_rule(
        name=data['name'],
        condition=data['condition'],
        action=data['action'],
        enabled=True
    )
    automation_manager.reload_rules()
    return flask.jsonify({'status': 'success', 'rule_id': rule_id})

@app.route('/api/automation/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Delete automation rule"""
    db.delete_rule(rule_id)
    automation_manager.reload_rules()
    return flask.jsonify({'status': 'success'})

@app.route('/api/schedule', methods=['POST'])
def schedule_device():
    """Schedule device action"""
    data = flask.request.json
    schedule_id = db.add_schedule(
        device_id=data['device_id'],
        action=data['action'],
        schedule_time=data['time']
    )
    return flask.jsonify({'status': 'success', 'schedule_id': schedule_id})

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms"""
    rooms = db.get_all_rooms()
    return flask.jsonify({'status': 'success', 'rooms': rooms})

@app.route('/api/rooms', methods=['POST'])
def add_room():
    """Add new room"""
    data = flask.request.json
    room_id = db.add_room(data['name'])
    return flask.jsonify({'status': 'success', 'room_id': room_id})

@app.route('/api/energy', methods=['GET'])
def get_energy_usage():
    """Get energy usage statistics"""
    stats = db.get_energy_stats()
    return flask.jsonify({'status': 'success', 'stats': stats})


from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        print("OTP sending to:", email)
        password = request.form["password"]

        user = db.get_user_by_email(email)

        if not user:
            flash("Email not registered.", "danger")

        elif not check_password_hash(user[3], password):
            flash("Wrong password.", "danger")

        else:
            session["user_id"] = user[0]
            session["username"] = user[1]

            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        success = db.register_user(username, email, password)

        if success:
            flash("Account created successfully!")
            return redirect(url_for("login"))

        flash("Username or Email already exists.")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    print("FORGOT PASSWORD ROUTE OPENED")
    if request.method == "POST":
        print("POST REQUEST RECEIVED")

        email = request.form["email"]

        print("OTP sending to:", email)

        # Check whether email exists
        user = db.get_user_by_email(email)

        if not user:
            flash("Email not registered.", "danger")
            return redirect(url_for("forgot_password"))

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP in session
        session["reset_email"] = email
        session["reset_otp"] = otp
        session["otp_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session["otp_attempts"] = 0

        # Send OTP
        if send_otp(email, otp):

            print("OTP SENT SUCCESSFULLY TO:", email)

            flash(
                "Verification code sent to your email.",
                "success"
            )

            return redirect(url_for("verify_otp"))

        else:

            print("OTP SEND FAILED")

            flash(
                "Unable to send verification email.",
                "danger"
            )

            return redirect(url_for("forgot_password"))


    return render_template("forgot_password.html")

@app.route("/verify_otp", methods=["GET","POST"])
def verify_otp():

    if "reset_otp" not in session:
        flash("Please request a new OTP.","danger")
        return redirect(url_for("forgot_password"))

    otp_time = datetime.strptime(
        session["otp_time"],
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > otp_time + timedelta(minutes=1):

        session.clear()

        flash("OTP expired after 1 minute. Please request another one.","danger")

        return redirect(url_for("forgot_password"))

    if request.method=="POST":

        entered=request.form["otp"]

        if entered==session["reset_otp"]:

            return redirect(url_for("reset_password"))

        session["otp_attempts"] += 1

        if session["otp_attempts"]>=3:

            session.clear()

            flash("Too many incorrect attempts.","danger")

            return redirect(url_for("forgot_password"))

        flash("Incorrect OTP.","danger")

    return render_template("verify_otp.html")
@app.route("/devices")
def devices():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("devices.html")

@app.route("/automation")
def automation_page():
    return flask.render_template("automation.html")


@app.route("/energy")
def energy():
    devices = db.get_devices()
    stats = db.get_energy_stats()

    return flask.render_template(
        "energy.html",
        devices=devices,
        stats=stats
    )

@app.route("/voice", methods=["GET", "POST"])
def voice():

    print("Voice page opened")

    response = ""

    if request.method == "POST":

        print("Start Listening button clicked")

        command = voice_assistant.get_voice_input()

        print("Command received:", command)

        if command:

            result = ai_assistant.process_command(command)

            print("AI Result:", result)

            if result["action"]:
                automation_manager.execute_action(result["action"])

            voice_assistant.text_to_speech(result["response"])

            response = result["response"]

        else:
            response = "No voice command detected."

    return render_template(
        "voice.html",
        response=response
    )

@app.route("/assistant", methods=["GET", "POST"])
def assistant():

    if request.method == "POST":

        command = request.form["command"]

        result = ai_assistant.process_command(command)

        return render_template(
            "assistant.html",
            response=result["response"]
        )

    return flask.render_template(
        "assistant.html",
        response=""
    )

@app.route("/security")
def security():
    return flask.render_template("security.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if "reset_email" not in session:
        flash("Please verify your OTP first.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password"))

        success = db.update_password(
            session["reset_email"],
            password
        )

        if success:

            session.pop("reset_email", None)
            session.pop("reset_otp", None)

            flash("Password changed successfully. Please login.", "success")

            return redirect(url_for("login"))

        flash("Unable to update password.", "danger")

    return render_template("reset_password.html")


@app.route("/resend_otp")
def resend_otp():

    if "reset_email" not in session:
        return redirect(url_for("forgot_password"))

    otp=str(random.randint(100000,999999))

    session["reset_otp"]=otp
    session["otp_time"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session["otp_attempts"]=0

    send_otp(session["reset_email"],otp)

    flash("A new OTP has been sent.","success")

    return redirect(url_for("verify_otp"))

if __name__ == "__main__":
    print("Starting Flask Server...")
    automation_manager.start_scheduler()
    app.run(host="127.0.0.1", port=5000, debug=True)