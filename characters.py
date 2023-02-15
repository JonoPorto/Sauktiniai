import sqlite3


conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT id, email FROM email_list")

changed_emails = []

for row in c.fetchall():
    email_id = row[0]
    email = row[1]
    email_lower = email.lower().encode('utf-8').decode('utf-8')
    if email != email_lower:
        c.execute("UPDATE email_list SET email = ? WHERE id = ?", (email_lower, email_id))
        changed_emails.append(email_lower)
conn.commit()
conn.close()
