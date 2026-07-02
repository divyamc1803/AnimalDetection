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