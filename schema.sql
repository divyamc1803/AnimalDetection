-- Animal Detection System - Database Schema
-- Run this to (re)set up MySQL for the app.
-- WARNING: This DROPS the existing database and all its data before recreating it.
--
-- From terminal:
--   mysql -u root -p < schema.sql
--
-- Or inside the MySQL shell:
--   mysql -u root -p
--   SOURCE /path/to/schema.sql;

DROP DATABASE IF EXISTS animal_detection;

CREATE DATABASE animal_detection;
USE animal_detection;

-- ---------------- USERS ----------------

CREATE TABLE IF NOT EXISTS Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------- UPLOADED IMAGES ----------------

CREATE TABLE IF NOT EXISTS UploadedImages (
    ImageID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    ImageName VARCHAR(255) NOT NULL,
    ImagePath VARCHAR(500) NOT NULL,
    UploadedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

-- ---------------- DETECTION RESULTS ----------------

CREATE TABLE IF NOT EXISTS DetectionResults (
    DetectionID INT AUTO_INCREMENT PRIMARY KEY,
    ImageID INT NOT NULL,
    AnimalName VARCHAR(100) NOT NULL,
    Confidence FLOAT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ImageID) REFERENCES UploadedImages(ImageID) ON DELETE CASCADE
);

-- Helpful indexes for lookups the app does often
CREATE INDEX idx_uploadedimages_userid ON UploadedImages(UserID);
CREATE INDEX idx_detectionresults_imageid ON DetectionResults(ImageID);

-- ---------------- REFRESH TOKENS ----------------

CREATE TABLE IF NOT EXISTS RefreshTokens (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UserId INT NOT NULL,
    TokenHash VARCHAR(255) NOT NULL,
    ExpiryDate DATETIME NOT NULL,
    IsRevoked BOOLEAN DEFAULT FALSE,
    IsUsed BOOLEAN DEFAULT FALSE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE INDEX idx_refreshtokens_tokenhash ON RefreshTokens(TokenHash);