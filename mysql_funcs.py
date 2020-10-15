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

_TABLES["products"] = (
    "CREATE TABLE `products` ("
    "`product_id` int(11) NOT NULL,"
    "`name` varchar(255) NOT NULL,"
    "`price` float NOT NULL,"
    "`expiry_date` date,"
    "`qty` int(11) NOT NULL,"
    "PRIMARY KEY (product_id)"
    ") ENGINE=InnoDB DEFAULT CHARSET=latin1;"
)

_TABLES["orders"] = (
    "CREATE TABLE `orders` ("
    "`id` int(11) NOT NULL AUTO_INCREMENT,"
    "`cust_name` varchar(255) DEFAULT NULL,"
    "`cust_email` varchar(255) DEFAULT NULL,"
    "`cust_phone` varchar(20) DEFAULT NULL,"
    "`total_amount` float NOT NULL,"
    "`date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    "PRIMARY KEY (id)"
    ")"
)

_TABLES["order_items"] = (
    "CREATE TABLE `order_items` ("
    "`id` int(11) NOT NULL AUTO_INCREMENT,"
    "`order_id` int(11) NOT NULL,"
    "`item_id` int(11) NOT NULL,"
    "`item_name` varchar(255) NOT NULL,"
    "`qty` int(11) NOT NULL,"
    "`unit_price` float NOT NULL,"
    "`sub_total` float NOT NULL,"
    "PRIMARY KEY (id)"
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


def get_table_data(table_name, *sort_by_column, search_dict=None, search_mode="AND"):
    cursor = new_cursor()
    query = f"SELECT * FROM {table_name}"
    if search_dict:
        query += " WHERE "
        for column_name in search_dict:
            query += f"{column_name} LIKE %s {search_mode} "
        if query.endswith(f"{search_mode} "):
            query = query[: -(len(search_mode) + 1)]
    if sort_by_column:
        query += " ORDER BY "
        for column, order in sort_by_column:
            query += f"{column} {order},"
    query = query.rstrip(",")

    if search_dict:
        cursor.execute(query, tuple(search_dict.values()))
    else:
        cursor.execute(query)

    values = [list(map(str, values)) for values in cursor.fetchall()]
    headings = [column[0] for column in cursor.description]

    if len(values) == 0:
        values.append(["" for _ in range(len(headings))])

    cursor.close()
    return values, headings
