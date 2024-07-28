import sqlite3
import bcrypt
conn = sqlite3.connect('instance/database.db')
print("Connected to database successfully")
password = "1234"
hashpassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
conn.execute('INSERT INTO admin(uname, password) VALUES ("praj" , "{{hashpassword}}" )')
conn.commit()
print("Created table successfully!")

conn.close()
