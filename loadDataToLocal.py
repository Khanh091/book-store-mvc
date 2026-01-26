import json
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="bookstore_db"
)

cursor = conn.cursor()

with open("db_seed.json", encoding="utf-8") as f:
    data = json.load(f)

sql = """
INSERT INTO auth_permission (id, name, content_type_id, codename)
VALUES (%s, %s, %s, %s)
"""

for item in data:
    if item["model"] == "auth.permission":
        cursor.execute(sql, (
            item["pk"],
            item["fields"]["name"],
            item["fields"]["content_type"],
            item["fields"]["codename"]
        ))

conn.commit()
cursor.close()
conn.close()
