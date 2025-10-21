USE dd_attendance;

-- Shifts table
CREATE TABLE IF NOT EXISTS shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default shifts
INSERT IGNORE INTO shifts (id, name, start_time, end_time, description) VALUES
(1, 'Morning', '08:00:00', '16:00:00', 'Morning shift 8AM - 4PM'),
(2, 'Evening', '16:00:00', '00:00:00', 'Evening shift 4PM - 12AM'),
(3, 'Night', '00:00:00', '08:00:00', 'Night shift 12AM - 8AM'),
(4, 'Flexible', '09:00:00', '17:00:00', 'Flexible office hours');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    privilege VARCHAR(20) DEFAULT 'User',
    card_number VARCHAR(50),
    department VARCHAR(100),
    shift_id INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shift_id) REFERENCES shifts(id),
    INDEX idx_user_id (user_id),
    INDEX idx_shift (shift_id)
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(100),
    timestamp DATETIME NOT NULL,
    event_type ENUM('IN', 'OUT', 'UNKNOWN') NOT NULL,
    status_code INT,
    status_description VARCHAR(100),
    device_type ENUM('HIKVISION', 'ZK', 'MANUAL') NOT NULL,
    device_ip VARCHAR(15) NOT NULL,
    device_location VARCHAR(100),
    verification_mode VARCHAR(50),
    shift_id INT,
    shift_name VARCHAR(50),
    is_shift_start BOOLEAN DEFAULT FALSE,
    is_shift_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shift_id) REFERENCES shifts(id),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_type (device_type),
    INDEX idx_event_type (event_type),
    INDEX idx_shift (shift_id),
    INDEX idx_shift_start (is_shift_start),
    INDEX idx_shift_end (is_shift_end),
    UNIQUE KEY unique_clock_record (user_id, timestamp, device_type, device_ip)
);

-- Device information table
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_type ENUM('HIKVISION', 'ZK') NOT NULL,
    device_ip VARCHAR(15) NOT NULL UNIQUE,
    device_name VARCHAR(100),
    device_location VARCHAR(100),
    device_model VARCHAR(50),
    serial_number VARCHAR(100),
    purpose ENUM('ENTRY', 'EXIT', 'BOTH') DEFAULT 'ENTRY',
    last_sync TIMESTAMP NULL,
    status ENUM('ONLINE', 'OFFLINE', 'MAINTENANCE') DEFAULT 'ONLINE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default devices
INSERT IGNORE INTO devices (device_type, device_ip, device_name, device_location, purpose) VALUES
('HIKVISION', '192.168.1.30', 'HikVision Face Reader Pro', 'Main Entrance', 'ENTRY'),
('ZK', '192.168.1.20', 'ZKTeco SpeedFace V5L', 'Main Exit', 'EXIT');