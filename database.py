import sqlite3
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class Database:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        db_folder = os.path.join(BASE_DIR, "database")
        os.makedirs(db_folder, exist_ok=True)

        self.db_path = os.path.join(db_folder, "smart_home.db")

        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):

        conn = self.connect()
        cursor = conn.cursor()

        # ---------------- USERS ----------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        # ---------------- DEVICES ----------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            room TEXT NOT NULL,
            status TEXT DEFAULT 'OFF'
        )
        """)

        # ---------------- ROOMS ----------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        """)

        # ---------------- AUTOMATION ----------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS automation_rules(
            id TEXT PRIMARY KEY,
            name TEXT,
            condition_text TEXT,
            action_text TEXT,
            enabled INTEGER DEFAULT 1
        )
        """)

        # ---------------- SCHEDULES ----------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules(
            id TEXT PRIMARY KEY,
            device_id TEXT,
            action TEXT,
            schedule_time TEXT
        )
        """)

        # ---------------- ENERGY ----------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS energy_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            energy_usage REAL,
            log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    # ===================================================
    # USER METHODS
    # ===================================================

    def register_user(self, username, email, password):
        conn = self.connect()
        cursor = conn.cursor()

        hashed_password = generate_password_hash(password)

        try:
            print("Registering:", username, email)

            cursor.execute(
                "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )

            conn.commit()
            print("User saved successfully")

            return True

        except Exception as e:
            print("Registration Error:", e)
            return False

        finally:
            conn.close()

    def login_user(self, email, password):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()


        if user and check_password_hash(user[3], password):
            return user

        return None

    def get_user(self, user_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,)
        )

        user = cursor.fetchone()

        conn.close()

        return user

    # ===================================================
    # DEVICE METHODS
    # ===================================================

    def add_device(self, name, device_type, room, status="OFF"):

        conn = self.connect()
        cursor = conn.cursor()

        device_id = str(uuid.uuid4())[:8]

        cursor.execute(
            """
            INSERT INTO devices
            (id,name,type,room,status)
            VALUES(?,?,?,?,?)
            """,
            (
                device_id,
                name,
                device_type,
                room,
                status
            )
        )

        conn.commit()
        conn.close()

        return device_id

    def get_all_devices(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM devices")

        rows = cursor.fetchall()

        conn.close()

        devices = []

        for row in rows:

            devices.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "room": row[3],
                "status": row[4]
            })

        return devices

    def get_devices(self):
        return self.get_all_devices()

    def get_device(self, device_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM devices WHERE id=?",
            (device_id,)
        )

        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "room": row[3],
                "status": row[4]
            }

        return None

    def update_device_status(self, device_id, status):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE devices SET status=? WHERE id=?",
            (status, device_id)
        )

        conn.commit()
        conn.close()

        return True

    def update_status(self, device_id, status):
        return self.update_device_status(device_id, status)

    def delete_device(self, device_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM devices WHERE id=?",
            (device_id,)
        )

        conn.commit()
        conn.close()

    def total_devices(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM devices")

        total = cursor.fetchone()[0]

        conn.close()

        return total

    # ===================================================
    # ROOM METHODS
    # ===================================================

    def add_room(self, name):

        conn = self.connect()
        cursor = conn.cursor()

        room_id = str(uuid.uuid4())[:8]

        cursor.execute(
            "INSERT INTO rooms(id,name) VALUES(?,?)",
            (room_id, name)
        )

        conn.commit()
        conn.close()

        return room_id

    def get_all_rooms(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM rooms")

        rows = cursor.fetchall()

        conn.close()

        rooms = []

        for row in rows:
            rooms.append({
                "id": row[0],
                "name": row[1]
            })

        return rooms

    def delete_room(self, room_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM rooms WHERE id=?",
            (room_id,)
        )

        conn.commit()
        conn.close()

    # ===================================================
    # AUTOMATION METHODS
    # ===================================================

    def add_rule(self, name, condition, action, enabled=True):

        conn = self.connect()
        cursor = conn.cursor()

        rule_id = str(uuid.uuid4())[:8]

        cursor.execute(
            """
            INSERT INTO automation_rules
            (id,name,condition_text,action_text,enabled)
            VALUES(?,?,?,?,?)
            """,
            (
                rule_id,
                name,
                condition,
                action,
                1 if enabled else 0
            )
        )

        conn.commit()
        conn.close()

        return rule_id

    def get_all_rules(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM automation_rules")

        rows = cursor.fetchall()

        conn.close()

        rules = []

        for row in rows:
            rules.append({
                "id": row[0],
                "name": row[1],
                "condition": row[2],
                "action": row[3],
                "enabled": bool(row[4])
            })

        return rules

    def delete_rule(self, rule_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM automation_rules WHERE id=?",
            (rule_id,)
        )

        conn.commit()
        conn.close()

            # ===================================================
    # SCHEDULE METHODS
    # ===================================================

    def add_schedule(self, device_id, action, schedule_time):

        conn = self.connect()
        cursor = conn.cursor()

        schedule_id = str(uuid.uuid4())[:8]

        cursor.execute(
            """
            INSERT INTO schedules
            (id,device_id,action,schedule_time)
            VALUES(?,?,?,?)
            """,
            (
                schedule_id,
                device_id,
                action,
                schedule_time
            )
        )

        conn.commit()
        conn.close()

        return schedule_id

    def get_all_schedules(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM schedules")

        rows = cursor.fetchall()

        conn.close()

        schedules = []

        for row in rows:
            schedules.append({
                "id": row[0],
                "device_id": row[1],
                "action": row[2],
                "schedule_time": row[3]
            })

        return schedules

    def delete_schedule(self, schedule_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM schedules WHERE id=?",
            (schedule_id,)
        )

        conn.commit()
        conn.close()

    # ===================================================
    # ENERGY METHODS
    # ===================================================

    def add_energy_log(self, device_id, energy_usage):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO energy_logs(device_id, energy_usage)
            VALUES(?,?)
            """,
            (device_id, energy_usage)
        )

        conn.commit()
        conn.close()

    def get_energy_stats(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT IFNULL(SUM(energy_usage),0) FROM energy_logs"
        )

        total_energy = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM devices"
        )

        total_devices = cursor.fetchone()[0]

        conn.close()

        return {
            "total_energy": total_energy,
            "total_devices": total_devices
        }

    # ===================================================
    # HELPER METHODS
    # ===================================================

    def clear_devices(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM devices")

        conn.commit()
        conn.close()

    def clear_rooms(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM rooms")

        conn.commit()
        conn.close()

    def clear_rules(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM automation_rules")

        conn.commit()
        conn.close()

    def clear_schedules(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM schedules")

        conn.commit()
        conn.close()

    def close(self):
        pass