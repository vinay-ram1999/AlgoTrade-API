import sqlite3

con = sqlite3.connect("Test.db")

cursor = con.cursor()

""" SQLITE Datatypes

Integer
Resl
Text
BLOBS (binary large objects like pics)
Null
"""

n = "vinay"; sn = "gazula"; sal = 0

#cursor.execute("CREATE TABLE employees(name TEXT, surname TEXT, salary REAL)")
#cursor.execute("INSERT INTO employees VALUES('Maria', 'Mayer', 1000000)")
#cursor.execute("INSERT INTO employees VALUES('Caria', 'Nayer', 2500000)")
#cursor.execute("INSERT INTO employees VALUES(?,?,?)", (n,sn,sal))
#con.commit()

cursor.execute("SELECT * FROM employees")
#cursor.fetchone()
db = cursor.fetchall()
print(db)
