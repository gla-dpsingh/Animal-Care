-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS animal_care;

-- Select the database to use
USE animal_care;

-- Table for user accounts
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone_number VARCHAR(15),
    address TEXT,
    profile_picture VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table for hospitals
CREATE TABLE Hospital (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table for medicinal information
CREATE TABLE Medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    uses TEXT,
    side_effects TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table for user reports
CREATE TABLE Report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    report_type ENUM('Medical', 'Behavioral', 'Other') NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Pending', 'In Progress', 'Resolved') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Table for video calls
CREATE TABLE VideoCall (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    scheduled_at DATETIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);


-- Table for storing information related to medicine prescriptions or recommendations
CREATE TABLE MedicineRecommendation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT,
    medicine_id INT,
    dosage TEXT,
    recommendation TEXT,
    FOREIGN KEY (report_id) REFERENCES Report(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES Medicine(id) ON DELETE CASCADE
);

-- Add indexes on frequently searched columns
CREATE INDEX idx_user_email ON Users(email);
CREATE INDEX idx_report_status ON Report(status);
CREATE INDEX idx_video_call_status ON VideoCall(status);
CREATE INDEX idx_medicine_name ON Medicine(name);
CREATE INDEX idx_hospital_name ON Hospital(name);

-- Command to drop a database if it exists (for development purposes)
-- DROP DATABASE IF EXISTS animal_care;
