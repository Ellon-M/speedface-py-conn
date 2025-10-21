#!/usr/bin/env python3
"""
Dependency verification script for Attendance System
"""
import importlib
import sys

def check_dependency(module_name, package_name=None):
    """Check if a dependency is installed"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"✗ {package_name or module_name} - {e}")
        return False

def main():
    print("Checking Attendance System Dependencies...")
    print("=" * 50)
    
    dependencies = [
        ("mysql.connector", "mysql-connector-python"),
        ("zk", "pyzk"),
        ("requests", "requests"),
        ("dotenv", "python-dotenv"),
        ("win32service", "pywin32"),
        ("wfastcgi", "wfastcgi"),
        ("dateutil", "python-dateutil"),
        ("pytz", "pytz"),
        ("cryptography", "cryptography"),
    ]
    
    all_ok = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_ok = False
    
    print("=" * 50)
    if all_ok:
        print("✓ All dependencies installed successfully!")
        return 0
    else:
        print("✗ Some dependencies are missing!")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())