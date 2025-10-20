import os
import requests
from dotenv import load_dotenv
import csv
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

load_dotenv()

class HikVisionDeviceManager:
    
    def __init__(self, ip=None, port=80, timeout=10):
        self.ip = os.getenv('HIK_DEVICE_IP', '192.168.1.30')
        self.port = int(os.getenv('HIK_DEVICE_PORT', 80))
        self.username = os.getenv('HIK_USERNAME', 'admin')
        self.password = os.getenv('HIK_PASSWORD', '')
        self.timeout = int(os.getenv('HIK_TIMEOUT', 10))
        self.device_location = os.getenv('HIK_DEVICE_LOCATION', 'Main Entrance')
        
        self.base_url = f"http://{self.ip}:{self.port}/ISAPI"
        self.session = None
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'attendance_db'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 3306))
        }

        self.log_dir = os.getenv('LOG_DIR', './logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        print(f"Initializing HikVisionDeviceManager for ENTRY reader at {self.ip}:{self.port}")

    def connect_to_db(self):
        """Establish connection to MySQL database"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def get_user_shift_info(self, user_id):
        """Get user's shift information from database"""
        db_connection = self.connect_to_db()
        if not db_connection:
            return None
            
        try:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.user_id, u.name, u.shift_id, s.name as shift_name, 
                       s.start_time, s.end_time
                FROM users u 
                LEFT JOIN shifts s ON u.shift_id = s.id 
                WHERE u.user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            return result
            
        except Error as e:
            print(f"Error fetching user shift info: {e}")
            return None
        finally:
            if db_connection:
                db_connection.close()

    def calculate_shift_date_range(self, timestamp, shift_start, shift_end):
        """
        Calculate the shift date range for a given timestamp and shift times
        Handles night shifts that span across two days
        """
        record_time = timestamp.time()
        record_date = timestamp.date()
        
        # Convert shift times to time objects if they're strings
        if isinstance(shift_start, str):
            shift_start = datetime.strptime(shift_start, '%H:%M:%S').time()
        if isinstance(shift_end, str):
            shift_end = datetime.strptime(shift_end, '%H:%M:%S').time()
        
        # For night shifts (end time < start time)
        if shift_end < shift_start:
            if record_time >= shift_start:  # After midnight, still same shift day
                shift_date = record_date
            else:  # Before midnight, previous day's shift
                shift_date = record_date - timedelta(days=1)
        else:
            # Normal shift (same day)
            shift_date = record_date
            
        return shift_date

    def determine_shift_event(self, user_id, timestamp, shift_info):
        """
        Determine if this clock event is a shift start or end
        Based on whether it's the first IN or last OUT for the shift day
        """
        if not shift_info:
            return 'IN', False, False
            
        db_connection = self.connect_to_db()
        if not db_connection:
            return 'IN', False, False
            
        try:
            cursor = db_connection.cursor()
            
            # Calculate shift date for this record
            shift_date = self.calculate_shift_date_range(
                timestamp, 
                shift_info['start_time'], 
                shift_info['end_time']
            )
            
            # For HikVision device (ENTRY), we're looking for the first IN event of the shift day
            # Check if this is the first IN event for this user's shift day
            cursor.execute("""
                SELECT timestamp 
                FROM attendance 
                WHERE user_id = %s 
                AND DATE(timestamp) = %s
                AND device_type = 'HIKVISION'
                AND event_type = 'IN'
                ORDER BY timestamp ASC 
                LIMIT 1
            """, (user_id, shift_date))
            
            result = cursor.fetchone()
            is_shift_start = False
            
            if result:
                # If this timestamp is earlier than or equal to the first recorded IN
                existing_first_in = result[0]
                if timestamp <= existing_first_in:
                    is_shift_start = True
                    # Update previous records to remove shift_start flag
                    cursor.execute("""
                        UPDATE attendance 
                        SET is_shift_start = FALSE 
                        WHERE user_id = %s 
                        AND DATE(timestamp) = %s
                        AND is_shift_start = TRUE
                    """, (user_id, shift_date))
            else:
                # First IN record for this shift day
                is_shift_start = True
            
            return 'IN', is_shift_start, False
            
        except Error as e:
            print(f"Error determining shift event: {e}")
            return 'IN', False, False
        finally:
            if db_connection:
                db_connection.close()

    def test_connections(self):
        """Test both device and database connections"""
        print("\nTesting HikVision connections...")
        print(f"Device Target: {self.ip}:{self.port}")
        print(f"Database Target: {self.db_config['host']}:{self.db_config['port']}")
        
        if self.connect_to_device():
            print("✓ HikVision device connection successful")
            self.disconnect_from_device()
        else:
            print("✗ HikVision device connection failed")
        
        db_conn = self.connect_to_db()
        if db_conn:
            print("✓ Database connection successful")
            db_conn.close()
        else:
            print("✗ Database connection failed")

    def connect_to_device(self):
        """Establish connection to the HikVision device"""
        try:
            print("Attempting to connect to HikVision device...")
            self.session = requests.Session()
            self.session.auth = (self.username, self.password)
            self.session.timeout = self.timeout
            
            response = self.session.get(f"{self.base_url}/System/deviceInfo")
            if response.status_code == 200:
                print("Successfully connected to HikVision device!")
                return True
            else:
                print(f"Failed to connect to HikVision device. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Failed to connect to HikVision device: {e}")
            return False

    def disconnect_from_device(self):
        """Close the session"""
        if self.session:
            self.session.close()
            print("Disconnected from HikVision device")

    def get_attendances(self):
        """Retrieve all attendance records from the HikVision device"""
        if not self.session:
            print("No active connection to HikVision device")
            return None
            
        try:
            print("Fetching attendance records from HikVision device...")
            
            # Get events from last 24 hours
            end_time = datetime.now()
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            url = f"{self.base_url}/AccessControl/AcsEvent?format=json"
            
            payload = {
                "AcsEventCond": {
                    "searchID": "1",
                    "searchResultPosition": 0,
                    "maxResults": 10000,
                    "major": 5,
                    "minor": 1,
                    "startTime": start_time_str,
                    "endTime": end_time_str
                }
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                events_data = response.json()
                events = events_data.get('AcsEvent', {}).get('InfoList', [])
                
                if isinstance(events, dict):
                    events = [events]
                    
                print(f"Successfully retrieved {len(events)} attendance records from HikVision")
                return events
            else:
                print(f"Error fetching HikVision attendance. Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching attendance from HikVision: {e}")
            return None

    def store_attendance_to_db(self):
        """Store attendance records from HikVision device to database with shift logic"""
        db_connection = self.connect_to_db()
        if not db_connection:
            return False
            
        attendances = self.get_attendances()
        if not attendances:
            print("No attendance records found on HikVision device")
            db_connection.close()
            return False
            
        try:
            cursor = db_connection.cursor()
            
            # Update device last sync
            cursor.execute("""
                INSERT INTO devices (device_type, device_ip, device_location, purpose, last_sync, status)
                VALUES ('HIKVISION', %s, %s, 'ENTRY', NOW(), 'ONLINE')
                ON DUPLICATE KEY UPDATE last_sync = NOW(), status = 'ONLINE'
            """, (self.ip, self.device_location))
            
            new_records_count = 0
            duplicate_records_count = 0
            error_records_count = 0
            shift_start_records = 0
            
            for record in attendances:
                try:
                    user_id = record.get('employeeNoString', 'Unknown')
                    timestamp_str = record.get('time', '')
                    
                    if not timestamp_str:
                        continue
                        
                    # Parse timestamp
                    timestamp_str = timestamp_str.split('+')[0]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
                    
                    # Get user shift information
                    shift_info = self.get_user_shift_info(user_id)
                    
                    # Determine event type and shift flags
                    event_type, is_shift_start, is_shift_end = self.determine_shift_event(
                        user_id, timestamp, shift_info
                    )
                    
                    # Get additional info
                    employee_name = record.get('name', f"User_{user_id}")
                    verification_mode = record.get('verificationMode', 'Face')
                    shift_id = None
                    shift_name = None
                    
                    if shift_info:
                        employee_name = shift_info['name']
                        shift_id = shift_info['shift_id']
                        shift_name = shift_info['shift_name']
                    
                    cursor.execute("""
                        INSERT INTO attendance (
                            user_id, employee_name, timestamp, event_type, 
                            status_description, device_type, device_ip, 
                            device_location, verification_mode,
                            shift_id, shift_name, is_shift_start, is_shift_end
                        ) VALUES (%s, %s, %s, %s, %s, 'HIKVISION', %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        employee_name,
                        timestamp,
                        event_type,
                        'Check-in',
                        self.ip,
                        self.device_location,
                        verification_mode,
                        shift_id,
                        shift_name,
                        is_shift_start,
                        is_shift_end
                    ))
                    
                    new_records_count += 1
                    if is_shift_start:
                        shift_start_records += 1
                    
                except Error as e:
                    if 'unique_clock_record' in str(e):
                        duplicate_records_count += 1
                    else:
                        print(f"Error inserting HikVision record for user {user_id}: {e}")
                        error_records_count += 1
                except Exception as e:
                    print(f"Unexpected error for HikVision record {user_id}: {e}")
                    error_records_count += 1
            
            db_connection.commit()
            print(f"HikVision attendance - New: {new_records_count}, Shift Starts: {shift_start_records}, Duplicates: {duplicate_records_count}, Errors: {error_records_count}")
            return new_records_count > 0
            
        except Error as e:
            print(f"Error storing HikVision attendance to database: {e}")
            return False
        finally:
            if db_connection:
                db_connection.close()

    def export_clocking_logs(self, filename=None):
        """Export attendance logs to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hikvision_attendance_{timestamp}.csv"

        log_path = os.path.join(self.log_dir, filename)

        print(f"Exporting HikVision attendance logs to {log_path}...")

        attendances = self.get_attendances()
        if not attendances:
            print("No HikVision attendance records found")
            return False

        try:
            with open(log_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'User ID', 'Timestamp', 'Employee Name', 'Event Type', 
                    'Device Type', 'Device IP', 'Device Location', 'Verification Mode',
                    'Shift Start', 'Shift End'
                ])

                for record in attendances:
                    user_id = record.get('employeeNoString', 'Unknown')
                    timestamp = record.get('time', '')
                    employee_name = record.get('name', '')
                    verification_mode = record.get('verificationMode', 'Face')
                    
                    if timestamp:
                        timestamp = timestamp.split('+')[0]
                    
                    # For CSV export, determine shift events
                    shift_info = self.get_user_shift_info(user_id)
                    timestamp_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") if timestamp else datetime.now()
                    event_type, is_shift_start, is_shift_end = self.determine_shift_event(
                        user_id, timestamp_obj, shift_info
                    )
                    
                    writer.writerow([
                        user_id,
                        timestamp,
                        employee_name,
                        event_type,
                        'HIKVISION',
                        self.ip,
                        self.device_location,
                        verification_mode,
                        'Yes' if is_shift_start else 'No',
                        'Yes' if is_shift_end else 'No'
                    ])

            print(f"Successfully exported {len(attendances)} HikVision records to {log_path}")
            return True

        except Exception as e:
            print(f"Error exporting HikVision logs: {str(e)}")
            return False