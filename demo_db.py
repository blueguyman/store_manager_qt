import json
import random
from decimal import Decimal
from datetime import datetime

import mysql_funcs


def fill_database():
    staff_ids = set()
    ticket_ids = set()
    product_ids = set()

    with open("demo_data.json") as fp:
        demo_data = json.load(fp)

    cursor = mysql_funcs.new_cursor()

    while len(staff_ids) < random.randint(10, 40):
        emp_id = None
        while emp_id is None or emp_id in staff_ids:
            emp_id = random.randint(1000, 9999)
        staff_ids.add(emp_id)

        name = (
            random.choice(demo_data["f_names"])
            + " "
            + random.choice(demo_data["l_names"])
        )
        salary = Decimal(random.randrange(10000, 100001, 1000))
        department = random.choice(
            [
                "cashier",
                "customer support",
                "stocker",
                "janitorial",
                "security",
                "management",
            ]
        )

        cursor.execute(
            "INSERT INTO staff VALUES (%s, %s, %s, %s)",
            (emp_id, name, salary, department),
        )

    while len(ticket_ids) < random.randint(50, 150):
        ticket_id = None
        while ticket_id is None or ticket_id in ticket_ids:
            ticket_id = random.randint(1000, 9999)
        ticket_ids.add(ticket_id)

        author = (
            random.choice(demo_data["f_names"])
            + " "
            + random.choice(demo_data["l_names"])
        )
        email = (
            author.lower().replace(" ", "_")
            + str(random.randint(1, 999))
            + "@gmail.com"
        )
        content = demo_data["lorem_ipsum"]
        status = random.choice(("unresolved", "resolved"))

        cursor.execute(
            "INSERT INTO ticket VALUES (%s, %s, %s, %s, %s)",
            (ticket_id, author, email, content, status),
        )

    while len(product_ids) < random.randint(15, 20):
        product_id = None
        while product_id is None or product_id in product_ids:
            product_id = random.randint(1000, 9999)
        product_ids.add(product_id)

        name = random.choice(demo_data["products"])
        price = Decimal(random.randint(3, 10))
        expiry = datetime.now().date()
        qty = random.randint(50, 500)

        cursor.execute(
            "INSERT INTO products VALUES (%s, %s, %s, %s, %s)",
            (product_id, name, price, expiry, qty),
        )

    cursor.close()
    mysql_funcs.commit()
