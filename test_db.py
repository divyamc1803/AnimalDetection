from database import connect_db

try:
    conn = connect_db()
    print("Connected Successfully!")
    conn.close()

except Exception as e:
    print(e)