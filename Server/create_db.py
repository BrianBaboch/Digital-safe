import sqlite3
from sqlite3 import Error

def sql_connection():
    try:
        con = sqlite3.connect('digital_safe.db')
        print("Connection is established: Database is created")
        return con
    except Error:
        print(Error)

def create_sql_tables(con):
    cur = con.cursor()
    cur.execute('''CREATE TABLE objects(id, active)''')
    cur.execute('''CREATE TABLE safe_keys(safe_key_ID, related_resource, object_id, start_date, end_date)''')
    con.commit()

def main():
    con = sql_connection()
    create_sql_tables(con)
    con.close()
try:
    main()
except:
    exit()