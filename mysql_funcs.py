import mysql.connector
from mysql.connector.cursor import MySQLCursor

import misc

_TABLES = {}

_TABLES["staff"] = (
    "CREATE TABLE staff ("
    "   emp_no INT,"
    "   name VARCHAR(50),"
    "   salary DECIMAL(13, 2),"
    "   department VARCHAR(50)"
    ")"
)

# fmt: off
_TABLES["account"] = (
    "CREATE TABLE account ("
    "   id INT PRIMARY KEY,"
    "   password_hash BINARY(64)"
    ")"
)
# fmt: on


def connect_to_mysql(host, user, password):
    cnx = mysql.connector.connect(host=host, user=user, password=password)
    misc.save_data("host", host, "mysql")
    misc.save_data("user", user, "mysql")
    misc.CACHE["cnx"] = cnx


def new_cursor() -> MySQLCursor:
    return misc.CACHE["cnx"].cursor()


def commit():
    misc.CACHE["cnx"].commit()


def rollback():
    misc.CACHE["cnx"].rollback()


def get_valid_dbs():
    cursor = new_cursor()
    cursor.execute("SHOW DATABASES")

    databases = [row[0] for row in cursor]
    valid_dbs = []

    for database in databases:
        cursor.execute(f"USE {database}")
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor]
        if sorted(tables) == sorted(list(_TABLES.keys())):
            valid_dbs.append(database)

    cursor.close()
    if len(valid_dbs) == 0:
        valid_dbs.append("")

    return valid_dbs


def create_new_db(db_name, window=None):
    cursor = new_cursor()

    cursor.execute(f"CREATE DATABASE {db_name}")
    cursor.execute(f"USE {db_name}")

    try:
        for table in _TABLES.values():
            cursor.execute(table)
        set_password(0, "0000")
        misc.save_data("database", db_name, "mysql")
        db_created = True
    except mysql.connector.Error as err:
        cursor.execute(f"DROP DATABASE {db_name}")
        misc.log(window, err)
        db_created = False
        rollback()

    commit()
    cursor.close()
    return db_created


def set_password(id_: int, password: str):
    cursor = new_cursor()
    cursor.execute(
        "INSERT INTO account values (%s, UNHEX(SHA2(%s, 512)))", (id_, password)
    )
    cursor.close()


def validate_password(id_: int, password: str) -> bool:
    cursor = new_cursor()

    cursor.execute("SELECT password_hash FROM account WHERE id = %s", (id_,))
    password_hash_actual = cursor.fetchone()[0]

    cursor.execute("SELECT UNHEX(SHA2(%s, 512))", (password,))
    password_hash_new = cursor.fetchone()[0]
    cursor.close()

    return password_hash_actual == password_hash_new