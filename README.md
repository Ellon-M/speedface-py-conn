# ZKTeco x HikVision Device Manager

A Python class for interacting with a ZKTeco Device as well as a HikVision Device and storing data in MySQL. Tested with a V5L SpeedFace Device

## Features

- Dual Device Support
- Retrieve users and attendance records
- Store data in MySQL database
- Real Time Synchronization
- Shift Based Tracking
- Windows Service

## Requirements

### Hardware
- Windows Server VM
- IIS Web Server
- ZKTeco Device (connected to a LAN)
- HikVision Face Reader
- MySQL database server

### Software
- Python 3.6+



## Configuration

1. Create `.env` file:

```ini
# Device Settings
ZK_DEVICE_IP=your_ip
HIK_DEVICE_IP=your_ip
ZK_DEVICE_PORT=4370
HIK_DEVICE_PORT=80
ZK_TIMEOUT=set_default_value
HIK_TIMEOUT=10

# Database Settings
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=yourpassword
DB_PORT=3306
```

2. Create database tables (automatically created on first run)

## Class Structure

### `ZKDeviceManager`

#### Key Methods:
| Method | Description |
|--------|-------------|
| `__init__()` | Initializes connection parameters |
| `connect_to_device()` | Connects to ZKTeco device |
| `disconnect_from_device()` | Closes device connection |
| `get_users()` | Retrieves all users from device |
| `get_attendances()` | Gets attendance records |
| `store_users_to_db()` | Syncs users to MySQL |
| `get_users_from_db()` | Retrieves users from MySQL |

## Usage


### Install and Start as a Windows Service

```bash
python attendance_service.py install

net start AttendanceSystem
```

## Project Structure

```
project/
├── .env                # Configuration
├── main.py             # Main application
└── zk_device/
    ├── __init__.py     # Package initialization
    └── manager.py      # ZKDeviceManager class
└── hik_device/
    ├── __init__.py     # Package initialization
    └── manager.py      # HikDeviceManager class
```

## Troubleshooting

- **Connection issues**: Verify device IP and network connectivity
- **Database errors**: Check MySQL credentials and permissions
- **Missing data**: Ensure device and database are properly synced
