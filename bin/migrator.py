import sqlite3
import sys

import pandas as pd

old = sqlite3.connect(sys.argv[1])
desks = pd.read_sql_query("SELECT * FROM desk ORDER BY date ASC", old)
sessions = pd.read_sql_query("SELECT * FROM session ORDER BY date ASC", old)
old.close()

new = sqlite3.connect(sys.argv[2])
new.execute("CREATE TABLE session(date TIMESTAMP NOT NULL, state SESSION NOT NULL)")
new.execute("CREATE TABLE desk(date TIMESTAMP NOT NULL, state DESK NOT NULL)")

for desk in desks.itertuples():
    state = "up" if desk.state == 1 else "down"
    print(f"INSERT INTO desk values({desk.date}, {state})")
    new.execute("INSERT INTO desk values(?, ?)", (desk.date, state))

for session in sessions.itertuples():
    state = "active" if session.active == 1 else "inactive"
    print(f"INSERT INTO session values({session.date}, {state})")
    new.execute("INSERT INTO session values(?, ?)", (session.date, state))

new.commit()

new.close()
