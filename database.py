import sqlite3
import os
import uuid


try:
    from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
except ImportError:
    import base64
    import hashlib
    import secrets

    def generate_password_hash(password, method="pbkdf2:sha256", salt_length=16):
        if method.startswith("pbkdf2:"):
            method_parts = method.split(":")
            hash_name = method_parts[1] if len(method_parts) > 1 else "sha256"
            iterations = int(method_parts[2]) if len(method_parts) > 2 else 260000
            salt = secrets.token_bytes(salt_length)
            salt_b64 = base64.b64encode(salt).decode("utf-8")
            derived = hashlib.pbkdf2_hmac(hash_name, password.encode("utf-8"), salt, iterations)
            hash_b64 = base64.b64encode(derived).decode("utf-8")
            return f"pbkdf2:{hash_name}:{iterations}${salt_b64}${hash_b64}"
        raise NotImplementedError(f"Unsupported password hashing method: {method}")

    def check_password_hash(password_hash, password):
        if not password_hash or "$" not in password_hash:
            return False

        prefix, _, remainder = password_hash.partition("$")
        if not prefix.startswith("pbkdf2:"):
            return False

        parts = remainder.split("$")
        if len(parts) != 2:
            return False

        salt_b64, hash_b64 = parts
        method_parts = prefix.split(":")
        hash_name = method_parts[1] if len(method_parts) > 1 else "sha256"
        iterations = int(method_parts[2]) if len(method_parts) > 2 else 260000
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        expected = hashlib.pbkdf2_hmac(hash_name, password.encode("utf-8"), salt, iterations)
        return base64.b64decode(hash_b64.encode("utf-8")) == expected


class Database:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        db_folder = os.path.join(BASE_DIR, "database")
        os.makedirs(db_folder, exist_ok=True)

        self.db_path = os.path.join(db_folder, "smart_home.db")
        self._conn = None

        self.init_db()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        self._conn = conn
        return conn

    def init_db(self):
        conn = self.connect()
        cursor = conn.cursor()

        # USERS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        # SETTINGS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            user_id INTEGER PRIMARY KEY,

            home_name TEXT DEFAULT 'My Smart Home',
            timezone TEXT DEFAULT 'Asia/Kolkata',
            language TEXT DEFAULT 'en',

            voice_enabled INTEGER DEFAULT 1,
            wake_word TEXT DEFAULT 'Hey AI',
            voice_gender TEXT DEFAULT 'female',
            voice_rate INTEGER DEFAULT 150,
            voice_volume INTEGER DEFAULT 90,

            automation_enabled INTEGER DEFAULT 1,
            check_interval INTEGER DEFAULT 30,
            max_rules INTEGER DEFAULT 50,

            notifications INTEGER DEFAULT 1,
            email_notifications INTEGER DEFAULT 1,
            two_factor INTEGER DEFAULT 0,

            FOREIGN KEY(user_id) REFERENCES users(id)
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

        print("Database initialized")

    #-------------------------------General Settings Table--------------------------------

    def get_general_settings(self, user_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM settings
        WHERE user_id=?
        """,(user_id,))

        row = cursor.fetchone()

        conn.close()

        if row:
         return dict(row)

        return {
          }
        
    #--------------------------------General Settings Update--------------------------------

    def update_general_settings(self, user_id, home_name, timezone, language):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE settings
        SET home_name=?,
            timezone=?,
            language=?
        WHERE user_id=?
        """,
       (
        home_name,
        timezone,
        language,
        user_id
       ))
 
        print("Rows updated:", cursor.rowcount)

        conn.commit()
        conn.close()






        #-------------------------------Update Settings--------------------------------
    def update_settings(self, user_id, home_name, timezone, language):

        conn = self.connect()
        try:
            cursor = conn.cursor()
        
            cursor.execute("""
            UPDATE settings
            SET home_name=?,
                timezone=?,
                language=?
            WHERE user_id=?
            """,
            (
            home_name,
            timezone,
            language,
            user_id
            ))
            
            print("Rows updated:", cursor.rowcount)

            conn.commit()
        except Exception as e:
            print("Update Settings Error:", e)
        finally:
            conn.close()
       

        #-----------------Default Settings----------------
    def create_default_settings(self, user_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR IGNORE INTO settings
        (
        user_id,
        home_name,
        timezone,
        language
        )
        VALUES (?, 'My Smart Home', 'Asia/Kolkata', 'en')
        """, (user_id,))

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

            cursor.execute("SELECT id, username, email FROM users")
            print("Users in database:", cursor.fetchall())

            print("User saved successfully")
            return True

        except sqlite3.IntegrityError:
            return "Email or username already exists."

        except Exception as e:
            print(e)
            return str(e)

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

    def get_user_by_email(self, email):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()
        conn.close()

        return user

    def get_user_by_id(self, user_id):

     conn = self.connect()
     cursor = conn.cursor()

     cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )

     user = cursor.fetchone()

     conn.close()

     return user

    def update_profile(self, user_id, name, email):

     conn = self.connect()
     cursor = conn.cursor()

     cursor.execute(
        """
        UPDATE users
        SET username = ?,
            email = ?
        WHERE id = ?
        """,
        (
            name,
            email,
            user_id
        )
     )

     conn.commit()

     print("Updated rows:", cursor.rowcount)

     conn.close()

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

    def update_password(self, email, new_password):
        conn = self.connect()
        cursor = conn.cursor()

        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (hashed_password, email)
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success
    
    

    def get_settings(self, user_id):

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
        SELECT home_name, timezone, language
        FROM settings
        WHERE user_id=?
        """, (user_id,))


        row = cursor.fetchone()

        conn.close()

        if row:
         return {
            "home_name": row["home_name"],
            "timezone": row["timezone"],
            "language": row["language"]
        }

        return {
        "home_name": "My Smart Home",
        "timezone": "Asia/Kolkata",
        "language": "en"
    }

    def update_language(self, user_id, language):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE settings
        SET language=?
        WHERE user_id=?
        """, (language, user_id))

        conn.commit()
        conn.close()


   
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
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            finally:
                self._conn = None