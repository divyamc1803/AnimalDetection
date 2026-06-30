import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- SQL SERVER CONNECTION ----------------

SERVER = "localhost,1433"
DATABASE = "AnimalDetectionDB"
USERNAME = "sa"
PASSWORD = "DB_Password"

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "TrustServerCertificate=yes;"
)


# ---------------- CONNECT DATABASE ----------------

def connect_db():

    return pyodbc.connect(connection_string)


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
            VALUES (?, ?, ?)
            """,
            username,
            email,
            hashed_password
        )

        conn.commit()

        return True

    except pyodbc.Error:

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
        WHERE Username = ?
        """,
        username
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
        WHERE Username = ?
        """,
        username
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row 