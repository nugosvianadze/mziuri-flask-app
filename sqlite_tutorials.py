import sqlite3


DB_PATH = "instances/test.db"

subj_id = 5
connection = sqlite3.connect(DB_PATH)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor.execute(f"""
select * from subjets where id = {subj_id}
""")

for subject in cursor.fetchall():
    print(subject["title"])

print(cursor.fetchall())
# result = cursor.fetchone()
# print(result[1], type(result))
connection.close()