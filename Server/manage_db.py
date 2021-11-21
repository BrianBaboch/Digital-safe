import sqlite3
from sqlite3 import Error

def sql_connection():
    try:
        con = sqlite3.connect('digital_safe.db', check_same_thread=False)
        print("Connection is established")
        return con
    except Error:
        print(Error)

def sql_select_object(con, obj):
    cur = con.cursor()
    cur.execute("SELECT * from objects where id=:obj", {"obj":obj})
    return(cur.fetchall())

def sql_select_key(con, key):
    cur = con.cursor()
    cur.execute("SELECT * from safe_keys where ressource_ID=:key", {"key":key})
    return(cur.fetchall())

def sql_select_obj_key(con, obj):
    cur = con.cursor()
    cur.execute("SELECT ressource_ID, description, object_id, start_date, end_date from safe_keys where object_id=:obj", {"obj":obj})
    return(cur.fetchall())
    
def sql_insert(con, obj, table):
    cur = con.cursor()
    if(table == "objects"):
        if(len(obj) >2):
            return
        cur.execute("insert into objects values (?, ?)", (obj[0], obj[1]))
    if(table == "safe_keys"):
        if(len(obj) >6):
            return
        cur.execute("insert into safe_keys values (?, ?, ?, ?, ?, ?)", (obj[0], obj[1], obj[2], obj[3], obj[4], obj[5]))
    con.commit()

def deactivate_object(con, obj_id):
    cur = con.cursor()
    cur.execute("UPDATE objects SET active = 0 where id =:id", {"id":obj_id})
    con.commit()