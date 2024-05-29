import mysql.connector

import create_db

# Connection parameters
host = "localhost"
user = "root"
passwd = "@nts28PtMySQL"
# database_name = "citizen_db"
database_name = "LocaLog_db"
# Connect to MySQL server
mydb = mysql.connector.connect(
    host=host,
    user=user,
    passwd=passwd,
)

# Create a cursor object
mycursor = mydb.cursor()
mycursor.execute(f"CREATE DATABASE {database_name}")
print(f"Database '{database_name}' created.")

# lệnh xóa DATABASE
# DROP DATABASE [the name of the database];

# # Check if the database already exists
# mycursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
# existing_databases = mycursor.fetchall()

# # If the database doesn't exist, create it
# if not existing_databases:
#     mycursor.execute(f"CREATE DATABASE {database_name}")
#     print(f"Database '{database_name}' created.")
# else:
#     print(f"Database '{database_name}' already exists.")
#     create_db

# Close the cursor and connection
mycursor.close()
mydb.close()