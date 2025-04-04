from ZKDevice.manager import ZKDeviceManager

def main():
    print("ZK Device System Starting...")
    
    manager = ZKDeviceManager()
    
    # Test connections first
    manager.test_connections()
    
    # Main workflow
    if manager.connect_to_device():
        try:
            # Get and store users
            if users := manager.get_users():
                print(f"\nFound {len(users)} users on device")
                if manager.store_users_to_db():
                    print("Successfully synchronized users to database")

                # Add your attendance processing logic here


                # Export logs to default filename (timestamp-based)
                manager.export_clocking_logs()

        except Exception as e:
            print(f"Error during operation: {e}")
        finally:
            manager.disconnect_from_device()
            print("\nDisconnected from device")
    else:
        print("Failed to connect to device. Exiting.")

if __name__ == "__main__":
    main()