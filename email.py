import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT Lithuania.id, serve, email, [call], [note] FROM Lithuania, email_list WHERE Lithuania.id = email_list.id")

id_input = input("Enter an id: ")

found_row = False
for row in c.fetchall():
    if str(row[0]) == id_input:
        found_row = True
        serve = row[1]
        if serve == 1:
            print(f"{row[3]}, turite atlikti privalomaja karo tarnyba. {row[4]}")
        elif serve == 2:
            print(f"{row[3]}, gali tekti atlikti privalomaja karo tarnyba, laukite tolimesniu nurodymu. {row[4]}")
        elif serve == 0:
            pass
        else:
            print(f"Error: serve value {serve} is not valid for id {id_input}")
        break

if not found_row:
    print(f"Error: id {id_input} not found.")

conn.close()
