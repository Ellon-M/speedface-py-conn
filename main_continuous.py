#!/usr/bin/env python3
"""
Production-ready continuous attendance system for Windows Server
"""

import time
import logging
import sys
import os
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

# Add the application directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ZKDevice.manager import ZKDeviceManager
from HikVisionDevice.manager import HikVisionDeviceManager

class AttendanceSystem:
    def __init__(self):
        self.sync_interval = 60  # seconds
        self.running = True
        self.setup_logging()
        
        # Initialize device managers
        self.hik_manager = HikVisionDeviceManager()
        self.zk_manager = ZKDeviceManager()
        
        self.logger.info("Attendance System initialized on Windows Server")

    def setup_logging(self):
        """Setup comprehensive logging for Windows"""
        log_dir = os.getenv('LOG_DIR', 'C:\\AttendanceSystem\\logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'attendance_system.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('AttendanceSystem')

    def test_connections(self):
        """Test all connections"""
        self.logger.info("Testing device connections...")
        
        # Test HikVision
        if self.hik_manager.connect_to_device():
            self.logger.info("✓ HikVision connection successful")
            self.hik_manager.disconnect_from_device()
        else:
            self.logger.error("✗ HikVision connection failed")
        
        # Test ZKTeco
        if self.zk_manager.connect_to_device():
            self.logger.info("✓ ZKTeco connection successful")
            self.zk_manager.disconnect_from_device()
        else:
            self.logger.error("✗ ZKTeco connection failed")

    def sync_attendance_data(self):
        """Synchronize attendance data from both devices"""
        sync_time = datetime.now()
        self.logger.info(f"Starting synchronization at {sync_time}")
        
        success_count = 0
        error_count = 0
        
        # Process HikVision (IN Reader)
        try:
            self.logger.info("Processing HikVision device...")
            if self.hik_manager.connect_to_device():
                if self.hik_manager.store_attendance_to_db():
                    success_count += 1
                    self.logger.info("HikVision data synchronized successfully")
                else:
                    error_count += 1
                    self.logger.warning("No new HikVision data")
                self.hik_manager.disconnect_from_device()
            else:
                error_count += 1
                self.logger.error("Failed to connect to HikVision")
        except Exception as e:
            error_count += 1
            self.logger.error(f"HikVision synchronization error: {e}")

        # Process ZKTeco (OUT Reader)
        try:
            self.logger.info("Processing ZKTeco device...")
            if self.zk_manager.connect_to_device():
                # Sync users first
                self.zk_manager.sync_users_to_db()
                
                if self.zk_manager.store_attendance_to_db():
                    success_count += 1
                    self.logger.info("ZKTeco data synchronized successfully")
                else:
                    error_count += 1
                    self.logger.warning("No new ZKTeco data")
                self.zk_manager.disconnect_from_device()
            else:
                error_count += 1
                self.logger.error("Failed to connect to ZKTeco")
        except Exception as e:
            error_count += 1
            self.logger.error(f"ZKTeco synchronization error: {e}")

        # Log synchronization results
        duration = (datetime.now() - sync_time).total_seconds()
        self.logger.info(f"Synchronization completed in {duration:.2f}s - Success: {success_count}, Errors: {error_count}")

        return success_count > 0

    def run_continuous(self):
        """Main continuous loop"""
        self.logger.info("Starting continuous attendance synchronization")
        self.test_connections()
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                success = self.sync_attendance_data()
                
                if success:
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                    self.logger.warning(f"Consecutive errors: {consecutive_errors}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.error("Too many consecutive errors, waiting before retry")
                        time.sleep(300)  # Wait 5 minutes before retry
                        consecutive_errors = 0
                
                # Wait for next sync interval
                for _ in range(self.sync_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Unexpected error in main loop: {e}")
                consecutive_errors += 1
                time.sleep(60)  # Wait 1 minute before retry

        self.logger.info("Attendance system stopped gracefully")

def main():
    """Main entry point"""
    system = AttendanceSystem()
    system.run_continuous()

if __name__ == "__main__":
    main()