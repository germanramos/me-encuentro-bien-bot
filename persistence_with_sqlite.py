from datetime import datetime

import sqlite3 as _sqlite3

from constants import Status, DB_FILE

_con = _sqlite3.connect(DB_FILE)
_cursorObj = _con.cursor()
_cursorObj.execute("CREATE TABLE IF NOT EXISTS people(chat_id integer PRIMARY KEY, time date, status integer, name text, supervisor text)")
_con.commit()
_cursorObj.execute("CREATE TABLE IF NOT EXISTS supervisors(username text PRIMARY KEY, chat_id integer)")
_con.commit()
_con.close()

def getConnection():
    con = _sqlite3.connect(DB_FILE)
    cursor = con.cursor()
    return con, cursor

def createPerson(chat_id, name, supervisor):
    con, cursor = getConnection()
    entities = (chat_id, datetime.now(), Status.ESPERANDO_A_HACER_PING.value, name, supervisor)
    cursor.execute('''INSERT OR REPLACE INTO people(chat_id, time, status, name, supervisor) VALUES(?, ?, ?, ?, ?)''', entities)
    con.commit()
    con.close()

def updatePerson(chat_id, status):
    con, cursor = getConnection()
    entities = (datetime.now(), status.value, chat_id)
    cursor.execute('''UPDATE people SET time=?, status=? WHERE chat_id=?''', entities)
    con.commit()
    con.close()

def personExists(chat_id):
    con, cursor = getConnection()
    cursor.execute(f"SELECT chat_id FROM people WHERE chat_id={chat_id}")
    rows = cursor.fetchall()
    con.close()
    return len(rows) > 0

def getAllPeople():
    con, cursor = getConnection()
    cursor.execute("SELECT * FROM people")
    rows = cursor.fetchall()
    con.close()
    return [ {"chat_id": r[0], "time": datetime.fromisoformat(r[1]), "status": Status(r[2]), "name": r[3], "supervisor": r[4]} for r in rows]

def createSupervisor(chat_id, username):
    con, cursor = getConnection()
    entities = (username, chat_id)
    cursor.execute('''INSERT OR REPLACE INTO supervisors(username, chat_id) VALUES(?, ?)''', entities)
    con.commit()
    con.close()

def getSupervisorChatId(username):
    con, cursor = getConnection()
    chat_id = None
    try:
        cursor.execute(f"SELECT chat_id FROM supervisors WHERE username='{username}'")
        chat_id = cursor.fetchone()[0]
    except Exception as e:
        pass
    con.close()
    return chat_id

def remove(chat_id, username):
    con, cursor = getConnection()
    cursor.execute(f"DELETE FROM people WHERE chat_id={chat_id}")
    cursor.execute(f"DELETE FROM supervisors WHERE username='{username}'")
    con.commit()
    con.close()