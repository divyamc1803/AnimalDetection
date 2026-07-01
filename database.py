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

    cursor.close()
    conn.close()