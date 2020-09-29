import mysql.connector
from mysql.connector.cursor import MySQLCursor

import misc

_TABLES = {}

# fmt: off
_TABLES["staff"] = (
    "CREATE TABLE staff ("
    "   emp_id INT PRIMARY KEY,"
    "   name VARCHAR(50) NOT NULL,"
    "   salary DECIMAL(13, 2) NOT NULL,"
    "   department VARCHAR(50)"
    ")"
)

_TABLES["account"] = (
    "CREATE TABLE account ("
    "   user VARCHAR(50) PRIMARY KEY,"
    "   password_hash BINARY(64)"
    ")"
)

_TABLES["ticket"] = (
    "CREATE TABLE ticket ("
    "   ticket_id INT PRIMARY KEY,"
    "   author VARCHAR(50) NOT NULL,"
    "   email VARCHAR(50),"
    "   content VARCHAR(2500),"
    '   status VARCHAR(50)'
    ")"
)

# fmt: on


def connect_to_mysql(host, user, password):
    cnx = mysql.connector.connect(
        host=host, user=user, password=password, use_pure=True
    )
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
        set_password("manager", "0000")
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


def set_password(user: str, password: str):
    cursor = new_cursor()
    cursor.execute("SELECT * FROM account WHERE user = %s", (user,))
    cursor.fetchall()
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO account values (%s, UNHEX(SHA2(%s, 512)))", (user, password)
        )
    else:
        cursor.execute(
            "UPDATE account SET password_hash = UNHEX(SHA2(%s, 512)) WHERE user = %s",
            (password, user),
        )
    cursor.close()
    commit()


def validate_password(user: str, password: str) -> bool:
    cursor = new_cursor()

    cursor.execute("SELECT password_hash FROM account WHERE user = %s", (user,))
    password_hash_actual = cursor.fetchone()[0]

    cursor.execute("SELECT UNHEX(SHA2(%s, 512))", (password,))
    password_hash_new = cursor.fetchone()[0]
    cursor.close()

    return password_hash_actual == password_hash_new


def get_table_data(table_name, *sort_by_column):
    cursor = new_cursor()
    query = f"SELECT * FROM {table_name}"
    if sort_by_column:
        query += " ORDER BY "
    for column, order in sort_by_column:
        query += f"{column} {order},"
    query = query.rstrip(",")
    cursor.execute(query)

    values = [list(map(str, values)) for values in cursor.fetchall()]
    headings = [column[0] for column in cursor.description]

    if len(values) == 0:
        values.append(["" for _ in range(len(headings))])

    cursor.close()
    return values, headings
