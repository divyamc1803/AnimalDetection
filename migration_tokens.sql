-- ============================================================
-- Animal Detection System - Database Migration
-- Script: Create RefreshTokens, AccessTokens, and Auto-Cleanup Event
-- ============================================================

-- Enable the MySQL Event Scheduler globally so automatic deletion works
SET GLOBAL event_scheduler = ON;

-- ---------------- REFRESH TOKENS ----------------
-- Used for secure session management and token rotation (7 days expiry)
CREATE TABLE IF NOT EXISTS RefreshTokens (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UserId INT NOT NULL,
    TokenHash VARCHAR(512) NOT NULL,
    ExpiryDate DATETIME NOT NULL,
    IsRevoked BOOLEAN DEFAULT FALSE,
    IsUsed BOOLEAN DEFAULT FALSE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE INDEX idx_refreshtokens_tokenhash ON RefreshTokens(TokenHash);
CREATE INDEX idx_refreshtokens_userid ON RefreshTokens(UserId);


-- ---------------- ACCESS TOKENS ----------------
-- Used for storing active access tokens (15 minutes expiry, auto-deleted)
CREATE TABLE IF NOT EXISTS AccessTokens (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UserId INT NOT NULL,
    TokenHash VARCHAR(512) NOT NULL,
    ExpiryDate DATETIME NOT NULL,
    IsRevoked BOOLEAN DEFAULT FALSE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES Users(UserID) ON DELETE CASCADE
);

CREATE INDEX idx_accesstokens_tokenhash ON AccessTokens(TokenHash);
CREATE INDEX idx_accesstokens_userid ON AccessTokens(UserId);


-- ---------------- AUTO-CLEANUP EVENT ----------------
-- Automatically purges expired access tokens and expired/revoked refresh tokens every minute
DROP EVENT IF EXISTS purge_expired_tokens;

CREATE EVENT purge_expired_tokens
ON SCHEDULE EVERY 1 MINUTE
DO
    DELETE FROM AccessTokens WHERE ExpiryDate < NOW() OR IsRevoked = TRUE;
