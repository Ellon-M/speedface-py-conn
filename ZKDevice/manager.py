import os
from dotenv import load_dotenv
from zk import ZK, const
import mysql.connector
from mysql.connector import Error

load_dotenv()

class ZKDeviceManager:
    
    """ Class to manage ZKTeco device (V5L SpeedFace) and MySQL database connection """

    def __init__(self, ip=None, port=4370, timeout=5):
        """Constructor to initialize the connection"""
        # Device connection settings w/ fallbacks
        self.ip = os.getenv('ZK_DEVICE_IP', '192.168.1.20')
        self.port = int(os.getenv('ZK_DEVICE_PORT', 4370))
        self.timeout = int(os.getenv('ZK_TIMEOUT', 5))
        self.conn = None
        self.zk = None
        self.db_connection = None
        
        # MySQL database configuration w/ fallbacks
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'zk_device_db'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 3306))
        }

        self.conn = None
        self.zk = None
        self.db_connection = None
        
        print(f"Initializing ZKDeviceManager for device at {self.ip}:{self.port}")

    def test_connections(self):
        """Test both device and database connections"""
        print("\nTesting connections...")
        print(f"Device Target: {self.ip}:{self.port}")
        print(f"Database Target: {self.db_config['host']}:{self.db_config['port']}")
        
        # Test device connection
        if self.connect_to_device():
            print("✓ Device connection successful")
            self.disconnect_from_device()
        else:
            print("✗ Device connection failed")
        
        # Test database connection
        if self.connect_to_db():
            print("✓ Database connection successful")

    def connect_to_device(self):
        """Establish connection to the ZKTeco device"""
        try:
            print("Attempting to connect to device...")
            self.zk = ZK(self.ip, port=self.port, timeout=self.timeout)
            self.conn = self.zk.connect()
            print("Successfully connected to the device!")
            return True
        except Exception as e:
            print(f"Failed to connect to device: {e}")
            return False

    def disconnect_from_device(self):
        """Terminate the connection"""
        if self.conn:
            try:
                print("Disconnecting from device...")
                self.conn.disconnect()
                print("Successfully disconnected from device!")
            except Exception as e:
                print(f"Error disconnecting from device: {e}")
        else:
            print("No active connection to disconnect")

    def get_users(self):
        """Retrieve all users from the device"""
        if not self.conn:
            print("No active connection to device")
            return None
            
        try:
            print("Fetching users from device...")
            users = self.conn.get_users()
            print(f"Successfully retrieved {len(users)} users from device")
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return None

    def get_attendances(self):
        """Retrieve all attendance records from the device"""
        if not self.conn:
            print("No active connection to device")
            return None
            
        try:
            print("Fetching attendance records from device...")
            attendances = self.conn.get_attendance()
            print(f"Successfully retrieved {len(attendances)} attendance records")
            return attendances
        except Exception as e:
            print(f"Error fetching attendance records: {e}")
            return None

    def connect_to_db(self):
        """Establish connection to MySQL database"""
        try:
            print("Connecting to MySQL database...")
            self.db_connection = mysql.connector.connect(**self.db_config)
            print("Successfully connected to MySQL database!")
            return True
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return False

    def store_users_to_db(self):
        """Store users from device to database"""
        if not self.connect_to_db():
            return False
            
        users = self.get_users()
        if not users:
            return False
            
        try:
            cursor = self.db_connection.cursor()
            
            # Create users table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    uid INT PRIMARY KEY,
                    user_id VARCHAR(50),
                    name VARCHAR(100),
                    privilege VARCHAR(20),
                    password VARCHAR(50),
                    group_id VARCHAR(50)
                )
            """)
            
            # Check and insert new users
            new_users_count = 0
            for user in users:
                # Check if user exists
                cursor.execute("SELECT uid FROM users WHERE uid = %s", (user.uid,))
                if not cursor.fetchone():
                    # Insert new user
                    privilege = 'User'
                    if user.privilege == const.USER_ADMIN:
                        privilege = 'Admin'
                        
                    cursor.execute("""
                        INSERT INTO users (uid, user_id, name, privilege, password, group_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user.uid, user.user_id, user.name, privilege, user.password, user.group_id))
                    new_users_count += 1
            
            self.db_connection.commit()
            print(f"Successfully stored {new_users_count} new users to database")
            return True
            
        except Error as e:
            print(f"Error storing users to database: {e}")
            return False
        finally:
            if self.db_connection:
                self.db_connection.close()
                print("Closed database connection")

    def get_users_from_db(self):
        """Retrieve all users from database"""
        if not self.connect_to_db():
            return None
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            print(f"Retrieved {len(users)} users from database")
            return users
        except Error as e:
            print(f"Error retrieving users from database: {e}")
            return None
        finally:
            if self.db_connection:
                self.db_connection.close()
                print("Closed database connection")
