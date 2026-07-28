# pyright: reportMissingImports=false
import flask
from abc import ABC, abstractmethod
from flask import (  # type: ignore[import-not-found]
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

import traceback
import json
import os
from datetime import datetime

import automation as automation_module

from database import Database
from voice import VoiceAssistant
from ai import AIAssistant
from automation import AutomationManager

app = Flask(__name__)
print("Template folder:", app.template_folder)
print("Root path:", app.root_path)
app.secret_key = "your-secret-key-here"

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


@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    user = db.get_user_by_email(email)

    if user:
        if check_password_hash(user[2], password):
            return redirect('/dashboard')
        else:
            return "Wrong password"
    else:
        return "User not found"


@app.route("/register", methods=["GET", "POST"])
def register():

    if flask.request.method == "POST":

        username = flask.request.form["username"]
        email = flask.request.form["email"]
        password = flask.request.form["password"]

        success = db.register_user(username, email, password)

        if success:
            flash("Account created successfully!")
            return redirect(url_for("login"))

        flash("Username or Email already exists.")

    return flask.render_template("register.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return flask.render_template(
        "dashboard.html",
        username=session["username"]
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if flask.request.method == "POST":

        email = flask.request.form["email"]

        # Add your password reset logic here later

        flash("Password reset link sent (demo).")
        return redirect(url_for("login"))

    return flask.render_template("forgot_password.html")

@app.route("/devices")
def devices():
    if "user" not in session:
        return redirect("/login")

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


if __name__ == "__main__":
    print("Starting Flask Server...")
    automation_manager.start_scheduler()
    app.run(host="127.0.0.1", port=5000, debug=True)