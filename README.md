# ZKTeco Device Manager

A Python class for interacting with a ZKTeco Device and storing data in MySQL. Tested with a V5L SpeedFace Device

## Features

- Connect to ZKTeco device
- Retrieve users and attendance records
- Store data in MySQL database
- Environment variable configuration

## Requirements

### Hardware
- ZKTeco Device (connected to a LAN)
- MySQL database server

### Software
- Python 3.6+
- Required packages:

```bash
pip install python-dotenv mysql-connector-python pyzk
```

## Configuration

1. Create `.env` file:

```ini
# Device Settings
ZK_DEVICE_IP=your_ip
ZK_DEVICE_PORT=4370
ZK_TIMEOUT=set_default_value

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


### Command Line

```bash
python main.py
```

## Project Structure

```
project/
├── .env                # Configuration
├── main.py             # Main application
└── zk_device/
    ├── __init__.py     # Package initialization
    └── manager.py      # ZKDeviceManager class
```

## Troubleshooting

- **Connection issues**: Verify device IP and network connectivity
- **Database errors**: Check MySQL credentials and permissions
- **Missing data**: Ensure device and database are properly synced