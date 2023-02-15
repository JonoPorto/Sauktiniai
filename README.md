# Etex

## DISCLAIMER Čia naudojami Lietuvos kariuomenės pateikti duomenys - šauktinių sąrašas. Šie duomenys yra vieši ir visiems laisvai prieinami.


Sveiki, čia mano darbas su LK šauktinių sąrašu.
Darbo tikslas - apdoroti turimus duomenis, pasižiūrėti kurie šauktiniai tarnaus, sukurti tariamus elektroninius laiškus.

Iš esmės viskas vyksta su viena lenta. Pirminiais nu'scrape'intais duomenimis turiu 6 lentas su Lietuvos didžiausiais miestais. Kiekviena lenta turi stulpelius:

**ID - šaukimo numeris**

**year - gimimo metai**

**name - vardo pirma raidė ir pavardė**

**note - komentaras apie šaukimą**

**queue - šauktinio eilės numeris**

**city - miestas**

| name       | year | id         |  note                                                                        | queue | city      |
|------------|------|------------|------------------------------------------------------------------------------|-------|-----------|
| P. GIKA    | 2001 | 5309020102 | iki 2023-02-01 privalote susisiekti ir pateikti savo duomenis Utenos KPKP    | 1     | Panevezys |
| S. GILYS   | 2001 | 7111095691 | iki 2023-01-23 privalote susisiekti ir pateikti savo duomenis Panevėžio KPKP | 2     | Panevezys |
| R. LEGAVEC | 2003 | 5227881844 | privalote skubiai susisiekti arba atvykti į Panevėžio KPKP                   | 3     | Panevezys |



Pirmas žingsnis - apjungti atskirų miestų lentas į vieną:
```sql
CREATE TABLE Lithuania AS
SELECT * FROM Vilnius
UNION
SELECT * FROM Kaunas
UNION
SELECT * FROM Alytus
UNION
SELECT * FROM Klaipeda
UNION
SELECT * FROM Panevezys
UNION
SELECT * FROM Siauliai;
```
Sukūriau šaukinius šauktiniui stulpelyje **call**
Šaukiniai yra šauktinių pavardės, kurių galūnės pakeistos į kreipinius. Pavyzdžiui.:

Ambrazeviči**us** - Ambrazevič**iau**

```sql
ALTER TABLE Lithuania
ADD COLUMN call TEXT;

UPDATE Lithuania
SET call =
CASE
  WHEN name LIKE '%IUS' THEN REPLACE(name, 'IUS', 'IAU')
  WHEN name LIKE '%YS' THEN REPLACE(name, 'YS', 'Y')
  WHEN name LIKE '%AS' THEN REPLACE(name, 'AS', 'AI')
  WHEN name LIKE '%IS' THEN REPLACE(name, 'IS', 'I')
  ELSE name
END;
END;
```

Šaukiniai bus naudojami siunčiant informacinius pranešimus šauktiniams.

Kitas žingsnis - išskirstyti šauktinius pagal jų šansus tarnauti. Žinome, kad Lietuvoje privalomąją karo prievolę 2023 m. atliks 3828 šauktiniai.

Žinoti šauktinių skaičių kiekviename mieste būtina, kad galėtume numatyti kiek proporcingai kiekviename mieste šauktinių turės tarnauti. Kiekvienas iš 6 miestų šaukia skirtingą šauktinių skaičių. Išsi'select'inti tuos skaičius galime šitaip:
```sql
SELECT city, COUNT(id) AS total
FROM Lithuania
GROUP BY city
```
Rezultatas: 
| Miestas   | Pašaukta |
|-----------|----------|
| Alytus    | 2667     |
| Kaunas    | 8008     |
| Klaipeda  | 4910     |
| Panevezys | 2989     |
| Siauliai  | 4026     |
| Vilnius   | 9722     |

Nustatydami ar šauktinis tarnaus vadovaujamės jo eilės numeriu **queue** ir žiūrime ar jis įkrenta į miesto kviečiamų šauktinių proporciją:
```sql
SELECT total FROM total_per_city WHERE city = 'Vilnius') * 3828 / (SELECT SUM(total) FROM total_per_city)
```
Kadangi nėra pateikiama informacijos kiek pašauktų jaunuolių yra netinkami tarnybai atlikti ar jos vengia, žiūrėdamas į praėjusių metų skaičius laikausi prielaidos, 
kad 20% tarnybos neatliks, net jei turėtų. Tai darau, nes šauktiniai esantys šiek tiek aukščiau sąraše (virš eilės numerio kvietimui) vis tiek gali tarnauti.

Galiausiai priskiriu indikatorių prie kiekvieno šauktinio.

1 - šauktinis tarnaus
2 - šauktinis galimai tarnaus (20% virš eilės numerio)
3- Šauktiniui tarnauti nereikės

```sql
ALTER TABLE Lithuania
ADD COLUMN serve INT DEFAULT 0;

WITH total_per_city AS (
SELECT city, COUNT(id) AS total
FROM Lithuania
GROUP BY city
),
city_thresholds AS (
SELECT city, total * 0.2 AS threshold
FROM total_per_city
)
UPDATE Lithuania
SET serve =
CASE
WHEN city = 'Vilnius' AND queue <= (
(SELECT total FROM total_per_city WHERE city = 'Vilnius') * 3828 / (SELECT SUM(total) FROM total_per_city)
) THEN 1
WHEN city = 'Vilnius' AND queue <= (
SELECT threshold FROM city_thresholds WHERE city = 'Vilnius'
) THEN 2
WHEN city = 'Kaunas' AND queue <= (
(SELECT total FROM total_per_city WHERE city = 'Kaunas') * 3828 / (SELECT SUM(total) FROM total_per_city)
) THEN 1
WHEN city = 'Kaunas' AND queue <= (
SELECT threshold FROM city_thresholds WHERE city = 'Kaunas'
) THEN 2
WHEN city = 'Klaipeda' AND queue <= (
(SELECT total FROM total_per_city WHERE city = 'Klaipeda') * 3828 / (SELECT SUM(total) FROM total_per_city)
) THEN 1
WHEN city = 'Klaipeda' AND queue <= (
SELECT threshold FROM city_thresholds WHERE city = 'Klaipeda'
) THEN 2
WHEN city = 'Siauliai' AND queue <= (
(SELECT total FROM total_per_city WHERE city = 'Siauliai') * 3828 / (SELECT SUM(total) FROM total_per_city)
) THEN 1
WHEN city = 'Siauliai' AND queue <= (
SELECT threshold FROM city_thresholds WHERE city = 'Siauliai'
) THEN 2
WHEN city = 'Panevezys' AND queue <= (
(SELECT total FROM total_per_city WHERE city = 'Panevezys') * 3828 / (SELECT SUM(total) FROM total_per_city)
) THEN 1
WHEN city = 'Panevezys' AND queue <= (
SELECT threshold FROM city_thresholds WHERE city = 'Panevezys'
) THEN 2
WHEN city = 'Alytus' AND queue <= (
(SELECT total FROM total_per_city WHERE city = 'Alytus') * 3828 / (SELECT SUM(total) FROM total_per_city)
) THEN 1
WHEN city = 'Alytus' AND queue <= (
SELECT threshold FROM city_thresholds WHERE city = 'Alytus'
) THEN 2
ELSE 0
END;
```


| name          | year | id         | note                                                                               | queue | city     | call          | serve |
|---------------|------|------------|------------------------------------------------------------------------------------|-------|----------|---------------|-------|
| A. ABROMAS    | 2000 | 8731044614 | iki 2023-01-18 08:00 privalote susisiekti ir pateikti savo duomenis Klaipėdos KPKP | 169   | Klaipeda | A. ABROMAI    | 1     |
| A. ABRUNHEIRO | 2004 | 2598131860 | šaukimo procedūros vykdomos, sekite nurodymus                                      | 5017  | Vilnius  | A. ABRUNHEIRO | 0     |
| A. ABRUTIS    | 2003 | 2133352978 | privalote skubiai susisiekti arba atvykti į Kauno KPKP                             | 1373  | Kaunas   | A. ABRUTI     | 2     |


Dabar sukurkime numanomų el. paštų lentą, kurios PK bus šauktinio ID, o **email** stulpelį sudarys šauktinio el. paštas sudarytas iš **name** ir priedo @gmail.com

```sql
CREATE TABLE email_list AS
SELECT id, LOWER(name) || '@gmail.com' AS email
FROM Lithuania;
```
Mūsų rezultatas:
| id         | email                         |
|------------|-------------------------------|
| 4522061282 | a. aleksa@gmail.com           |
| 8098941352 | a. aleksandraviČius@gmail.com |
| 2046721099 | a. aleksandraviČius@gmail.com |

SQLite **LOWER** funkcija veikia tik su ASCII koduote, tačiau lietuviškos raidės yra koduojamos UTF-8.
Tai galime išspręsti su python kodu:
```python
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
```


Dabar mūsų duomenys atrodys šitaip: 

| id         | email                         |
|------------|-------------------------------|
| 4522061282 | a. aleksa@gmail.com           |
| 8098941352 | a. aleksandravičius@gmail.com |
| 2046721099 | a. aleksandravičius@gmail.com |

Galiausiai suformuojame tekstą elektroniniam laiškui siųsti:

```python
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
```
