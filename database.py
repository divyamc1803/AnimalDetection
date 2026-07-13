import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- MYSQL CONNECTION ----------------

HOST = "localhost"
DATABASE = "animal_detection"
USERNAME = "root"
PASSWORD = ""


# ---------------- CONNECT DATABASE ----------------

def connect_db():

    return mysql.connector.connect(
        host=HOST,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )


# ---------------- REGISTER USER ----------------

def register_user(username, email, password):

    conn = connect_db()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(
        password,
        method="pbkdf2:sha256"
    )

    try:

        cursor.execute(
            """
            INSERT INTO Users
            (Username, Email, PasswordHash)
            VALUES (%s, %s, %s)
            """,
            (
                username,
                email,
                hashed_password
            )
        )

        conn.commit()

        return True

    except mysql.connector.Error:

        return False

    finally:

        cursor.close()
        conn.close()


# ---------------- LOGIN USER ----------------

def login_user(username, password):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT Username, PasswordHash
        FROM Users
        WHERE Username = %s
        """,
        (username,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    if check_password_hash(row[1], password):
        return row[0]

    return None


# ---------------- GET USER ----------------

def get_user(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT UserID,
               Username,
               Email,
               CreatedAt
        FROM Users
        WHERE Username = %s
        """,
        (username,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row


# ---------------- GET USER ID ----------------

def get_user_id(username):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT UserID
        FROM Users
        WHERE Username = %s
        """,
        (username,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return row[0]

    return None


# ---------------- SAVE UPLOADED IMAGE ----------------

def save_uploaded_image(user_id, image_name, image_path):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO UploadedImages
        (UserID, ImageName, ImagePath)
        VALUES (%s, %s, %s)
        """,
        (
            user_id,
            image_name,
            image_path
        )
    )

    conn.commit()

    image_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return image_id
 # ---------------- SAVE DETECTION RESULT ----------------

def save_detection_result(image_id, animal_name, confidence):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO DetectionResults
        (ImageID, AnimalName, Confidence)
        VALUES (%s, %s, %s)
        """,
        (
            image_id,
            animal_name,
            confidence
        )
    )

    conn.commit()

    cursor.close()
    conn.close()
    # ---------------- GET IMAGE ID ----------------

def get_image_id(image_name):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ImageID
        FROM UploadedImages
        WHERE ImageName = %s
        ORDER BY ImageID DESC
        LIMIT 1
        """,
        (image_name,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return row[0]

    return None

# ---------------- GET UPLOAD HISTORY ----------------

def get_upload_history(user_id):

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            ImageID,
            UserID,
            ImageName,
            ImagePath,
            UploadedAt
        FROM UploadedImages
        WHERE UserID = %s
        ORDER BY UploadedAt DESC
    """, (user_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

# ---------------- GET DETECTION RESULTS ----------------

def get_detection_results(image_id):

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            DetectionID,
            AnimalName,
            Confidence,
            CreatedAt
        FROM DetectionResults
        WHERE ImageID = %s
    """, (image_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

# ---------------- DELETE IMAGE ----------------

def delete_uploaded_image(image_id, user_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM UploadedImages
        WHERE ImageID = %s AND UserID = %s
    """, (image_id, user_id))

    conn.commit()

    deleted = cursor.rowcount > 0

    cursor.close()
    conn.close()

    return deleted

# ---------------- CLEAR ALL HISTORY ----------------

def clear_upload_history(user_id):

    conn = connect_db()
    cursor = conn.cursor()

    # Remove detection results tied to this user's images first
    cursor.execute("""
        DELETE dr FROM DetectionResults dr
        INNER JOIN UploadedImages ui ON dr.ImageID = ui.ImageID
        WHERE ui.UserID = %s
    """, (user_id,))

    cursor.execute("""
        DELETE FROM UploadedImages
        WHERE UserID = %s
    """, (user_id,))

    conn.commit()

    deleted = cursor.rowcount

    cursor.close()
    conn.close()

    return deleted

    # ---------------- GET USER PROFILE ----------------

def get_user_profile(username):

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            UserID,
            Username,
            Email,
            CreatedAt
        FROM Users
        WHERE Username = %s
    """, (username,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row


# ---------------- REFRESH TOKEN OPERATIONS ----------------

import hashlib

def hash_token(token: str) -> str:
    """
    Cryptographically hashes a refresh token string using SHA-256.
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def save_refresh_token(user_id, token_hash, expiry_date):
    """
    Saves a new hashed refresh token in the database.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO RefreshTokens (UserId, TokenHash, ExpiryDate, IsRevoked, IsUsed)
            VALUES (%s, %s, %s, FALSE, FALSE)
            """,
            (user_id, token_hash, expiry_date)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error saving refresh token: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_refresh_token(token_hash):
    """
    Retrieves refresh token details by its hash.
    """
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT Id, UserId, TokenHash, ExpiryDate, IsRevoked, IsUsed, CreatedAt
            FROM RefreshTokens
            WHERE TokenHash = %s
            """,
            (token_hash,)
        )
        row = cursor.fetchone()
        return row
    except mysql.connector.Error as e:
        print(f"Error fetching refresh token: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def mark_refresh_token_used(token_id):
    """
    Marks a refresh token as used.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE RefreshTokens
            SET IsUsed = TRUE
            WHERE Id = %s
            """,
            (token_id,)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error marking refresh token as used: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def revoke_refresh_token(token_id):
    """
    Revokes a specific refresh token.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE RefreshTokens
            SET IsRevoked = TRUE
            WHERE Id = %s
            """,
            (token_id,)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error revoking refresh token: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def revoke_all_user_tokens(user_id):
    """
    Revokes all refresh tokens for a user (used during reuse detection).
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE RefreshTokens
            SET IsRevoked = TRUE
            WHERE UserId = %s AND IsRevoked = FALSE
            """,
            (user_id,)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error revoking all tokens for user {user_id}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_active_refresh_token(user_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT Id, TokenHash, ExpiryDate FROM RefreshTokens
            WHERE UserId = %s AND IsRevoked = FALSE AND ExpiryDate > NOW()
            LIMIT 1
            """,
            (user_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting active refresh token: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_access_token(user_id, token, expiry_date):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO AccessTokens (UserId, TokenHash, ExpiryDate, IsRevoked)
            VALUES (%s, %s, %s, FALSE)
            """,
            (user_id, token, expiry_date)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving access token: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def is_access_token_revoked(token):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT Id FROM AccessTokens WHERE TokenHash = %s AND IsRevoked = TRUE",
            (token,)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking access token revocation: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def revoke_access_token(token):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE AccessTokens SET IsRevoked = TRUE WHERE TokenHash = %s",
            (token,)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error revoking access token: {e}")
        return False
    finally:
        cursor.close()
        conn.close()