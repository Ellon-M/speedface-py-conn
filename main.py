from ZKDevice.manager import ZKDeviceManager
from HikVisionDevice.manager import HikVisionDeviceManager
from datetime import datetime

def main():
    print("=== Dual Device Attendance System ===")
    print("HikVision (IN Reader) + ZKTeco (OUT Reader)")
    print(f"Execution started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize device managers
    hik_manager = HikVisionDeviceManager()
    zk_manager = ZKDeviceManager()
    
    # Test connections
    print("=== Connection Tests ===")
    hik_manager.test_connections()
    zk_manager.test_connections()
    
    # Process HikVision (IN Reader)
    print("\n=== Processing HikVision (IN Reader) ===")
    if hik_manager.connect_to_device():
        try:
            if hik_manager.store_attendance_to_db():
                print("✓ HikVision attendance data stored successfully")
            else:
                print("✗ No new HikVision attendance data")
                
            hik_manager.export_clocking_logs()
            
        except Exception as e:
            print(f"✗ Error during HikVision processing: {e}")
        finally:
            hik_manager.disconnect_from_device()
    else:
        print("✗ Failed to connect to HikVision device")
    
    # Process ZKTeco (OUT Reader)
    print("\n=== Processing ZKTeco (OUT Reader) ===")
    if zk_manager.connect_to_device():
        try:
            # Sync users first
            if zk_manager.sync_users_to_db():
                print("✓ ZKTeco users synchronized")
            
            if zk_manager.store_attendance_to_db():
                print("✓ ZKTeco attendance data stored successfully")
            else:
                print("✗ No new ZKTeco attendance data")
                
            zk_manager.export_clocking_logs()
            
        except Exception as e:
            print(f"✗ Error during ZKTeco processing: {e}")
        finally:
            zk_manager.disconnect_from_device()
    else:
        print("✗ Failed to connect to ZKTeco device")
    
    print(f"\nExecution completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=== System Ready ===")

if __name__ == "__main__":
    main()