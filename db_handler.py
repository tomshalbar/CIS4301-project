from MARIADB_CREDS import DB_CONFIG
from mariadb import connect
from models.RentalHistory import RentalHistory
from models.Waitlist import Waitlist
from models.Item import Item
from models.Rental import Rental
from models.Customer import Customer
from datetime import date, timedelta


conn = connect(
    user=DB_CONFIG["username"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    database=DB_CONFIG["database"],
    port=DB_CONFIG["port"],
)

cur = conn.cursor()


def add_item(new_item: Item = None):
    """
    new_item - An Item object containing a new item to be inserted into the DB in the item table.
        new_item and its attributes will never be None.
    """

    """new_item = Item(item_id=item_id, product_name=product_name, brand=brand, category=category,
                    manufact=manufact, current_price=current_price, start_year=start_year, num_owned=num_owned)"""

    item_sk_query = f"SELECT MAX(i_item_sk) FROM item;"
    cur.execute(item_sk_query)
    max_sk = cur.fetchone()[0]
    new_item_sk = max_sk + 1

    new_item_rec_start_date = f"'{new_item.start_year}-01-01'"

    insert_query = f"INSERT INTO item(i_item_sk, i_item_id, i_rec_start_date, i_product_name, i_brand, i_category, i_manufact, i_current_price, i_num_owned) VALUES ({new_item_sk}, '{new_item.item_id}', {new_item_rec_start_date}, '{new_item.product_name}', '{new_item.brand}', '{new_item.category}', '{new_item.manufact}', {new_item.current_price}, {new_item.num_owned})"

    cur.execute(insert_query)


def parse_address(address: str):
    components = address.split(",")
    street_number, street_name = components[0].split(" ", 1)
    city = components[1].strip()
    state, zipcode = components[2].strip().split(" ")

    return street_number, street_name, city, state, zipcode


def add_customer(new_customer: Customer = None):
    """
    new_customer - A Customer object containing a new customer to be inserted into the DB in the customer table.
        new_customer and its attributes will never be None.
    """

    cur.execute(f"SELECT MAX(ca_address_sk) FROM customer_address;")
    address_sk = cur.fetchone()[0] + 1
    address_parts = parse_address(new_customer.address)
    cur.execute(
        f"INSERT INTO customer_address(ca_address_sk, ca_street_number, ca_street_name, ca_city, ca_state, ca_zip) VALUES ({address_sk}, {address_parts[0]}, '{address_parts[1]}', '{address_parts[2]}', '{address_parts[3]}', {address_parts[4]})"
    )

    cur.execute(f"SELECT MAX(c_customer_sk) FROM customer;")
    new_cust_sk = cur.fetchone()[0] + 1
    first_name, last_name = new_customer.name.split(" ")
    insert_query = f"INSERT INTO customer(c_customer_sk, c_customer_id, c_first_name, c_last_name, c_email_address, c_current_addr_sk) VALUES({new_cust_sk}, '{new_customer.customer_id}', '{first_name}', '{last_name}', '{new_customer.email}', {address_sk})"
    cur.execute(insert_query)


def edit_customer(original_customer_id: str = None, new_customer: Customer = None):
    """
    original_customer_id - A string containing the customer id for the customer to be edited.
    new_customer - A Customer object containing attributes to update. If an attribute is None, it should not be altered.
    """

    if new_customer.email is not None:
        cur.execute(
            f"UPDATE Customer SET c_email_address='{new_customer.email}' WHERE c_customer_id='{original_customer_id}'"
        )
    if new_customer.name is not None:
        first_name, last_name = new_customer.name.split(" ")
        cur.execute(
            f"UPDATE Customer SET c_first_name='{first_name}', c_last_name='{last_name}' WHERE c_customer_id='{original_customer_id}'"
        )
    if new_customer.address is not None:
        cur.execute(
            f"SELECT c_current_addr_sk FROM Customer WHERE c_customer_id='{original_customer_id}'"
        )
        add_sk = cur.fetchone()[0]
        address_parts = parse_address(new_customer.address)
        cur.execute(
            f"UPDATE customer_address SET ca_street_number={address_parts[0]}, ca_street_name='{address_parts[1]}', ca_city='{address_parts[2]}', ca_state='{address_parts[3]}', ca_zip={address_parts[4]} WHERE ca_address_sk='{add_sk}'"
        )
    if new_customer.customer_id is not None:
        cur.execute(
            f"UPDATE Customer SET c_customer_id='{new_customer.customer_id}' WHERE c_customer_id='{original_customer_id}'"
        )


def rent_item(item_id: str = None, customer_id: str = None):
    """
    item_id - A string containing the Item ID for the item being rented.
    customer_id - A string containing the customer id of the customer renting the item.
    """
    rental_date = date.today().isoformat()
    due_date = (date.today() + timedelta(days=14)).isoformat()
    cur.execute(
        f"INSERT INTO rental(item_id, customer_id, rental_date, due_date) VALUES ('{item_id}', '{customer_id}', '{rental_date}', '{due_date}')"
    )


def waitlist_customer(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's new place in line.
    """
    place = line_length(item_id) + 1
    cur.execute(
        f"INSERT INTO waitlist(item_id, customer_id, place_in_line) VALUES ('{item_id}', '{customer_id}', {place})"
    )
    return place


def update_waitlist(item_id: str = None):
    """
    Removes person at position 1 and shifts everyone else down by 1.
    """
    cur.execute(f"DELETE FROM waitlist WHERE item_id='{item_id}' AND place_in_line=1")

    cur.execute(
        f"UPDATE waitlist SET place_in_line = place_in_line - 1 WHERE item_id='{item_id}'"
    )


def return_item(item_id: str = None, customer_id: str = None):
    """
    Moves a rental from rental to rental_history with return_date = today.
    """
    cur.execute(
        f"SELECT * FROM rental WHERE item_id='{item_id}' AND customer_id='{customer_id}'"
    )
    rental_data = cur.fetchone()
    todays_date = date.today().isoformat()
    cur.execute(
        f"INSERT INTO rental_history(item_id, customer_id, rental_date, due_date, return_date) VALUES ('{rental_data[0]}', '{rental_data[1]}', '{rental_data[2].isoformat()}', '{rental_data[3].isoformat()}', '{todays_date}')"
    )
    cur.execute(
        f"DELETE FROM rental WHERE item_id='{item_id}' AND customer_id='{customer_id}'"
    )


def grant_extension(item_id: str = None, customer_id: str = None):
    """
    Adds 14 days to the due_date.
    """
    cur.execute(
        f"UPDATE rental SET due_date=due_date + INTERVAL 14 DAY WHERE item_id='{item_id}' AND customer_id='{customer_id}'"
    )


def get_filtered_items(
    filter_attributes: Item = None,
    use_patterns: bool = False,
    min_price: float = -1,
    max_price: float = -1,
    min_start_year: int = -1,
    max_start_year: int = -1,
) -> list[Item]:
    """
    Returns a list of Item objects matching the filters.
    """
    where_clause = f"WHERE"
    where_clause_used = 0
    comp = "LIKE" if use_patterns else "="
    if filter_attributes.item_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" i_item_id {comp} '{filter_attributes.item_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND i_item_id {comp} '{filter_attributes.item_id}'"
            )

    if filter_attributes.product_name is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause
                + f" i_product_name {comp} '{filter_attributes.product_name}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause
                + f" AND i_product_name {comp} '{filter_attributes.product_name}'"
            )

    if filter_attributes.brand is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" i_brand {comp} '{filter_attributes.brand}'"
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND i_brand {comp} '{filter_attributes.brand}'"
            )

    if filter_attributes.manufact is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" i_manufact {comp} '{filter_attributes.manufact}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND i_manufact {comp} '{filter_attributes.manufact}'"
            )

    if filter_attributes.category is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" i_category {comp} '{filter_attributes.category}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND i_category {comp} '{filter_attributes.category}'"
            )

    if min_price > 0:
        if where_clause_used == False:
            where_clause = where_clause + f" i_current_price >= {min_price}"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND i_current_price >= {min_price}"

    if max_price > 0:
        if where_clause_used == False:
            where_clause = where_clause + f" i_current_price <= {max_price}"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND i_current_price <= {max_price}"

    if min_start_year > 0:
        min_start_date = f"{min_start_year}-01-01"
        if where_clause_used == False:
            where_clause = where_clause + f" i_rec_start_date >= '{min_start_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND i_rec_start_date >= '{min_start_date}'"

    if max_start_year > 0:
        max_start_date = f"{max_start_year + 1}-01-01"
        if where_clause_used == False:
            where_clause = where_clause + f" i_rec_start_date < '{max_start_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND i_rec_start_date < '{max_start_date}'"

    query = f"SELECT * FROM item {where_clause};"
    cur.execute(query)

    results = []
    for row in cur:
        found_item = Item(
            item_id=row[1].strip(),
            product_name=row[3].strip(),
            brand=row[4].strip(),
            category=row[6].strip(),
            manufact=row[7].strip(),
            current_price=row[8],
            start_year=row[2].year,
            num_owned=row[9],
        )
        results.append(found_item)

    return results


def get_filtered_customers(
    filter_attributes: Customer = None, use_patterns: bool = False
) -> list[Customer]:
    """
    Returns a list of Customer objects matching the filters.
    """
    where_clause = f"WHERE"
    where_clause_used = 0
    comp = "LIKE" if use_patterns else "="
    if filter_attributes.customer_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause
                + f" c_customer_id {comp} '{filter_attributes.customer_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause
                + f" AND c_customer_id {comp} '{filter_attributes.customer_id}'"
            )
    if filter_attributes.name is not None:
        split_name = filter_attributes.name.split(" ")
        first_name = split_name[0]
        last_name = None
        if len(split_name) > 1:
            last_name = " ".join(split_name[1:])

        if where_clause_used == False:
            where_clause = where_clause + f" c_first_name {comp} '{first_name}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND c_first_name {comp} '{first_name}'"

        if last_name:
            where_clause = where_clause + f" AND c_last_name {comp} '{last_name}'"

    if filter_attributes.email is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" c_email_address {comp} '{filter_attributes.email}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause
                + f" AND c_email_address {comp} '{filter_attributes.email}'"
            )

    ## need to implament address logic. Not sure how to do it yet.

    query = f"SELECT * FROM Customer {where_clause};"
    cur.execute(query)

    results = []
    for row in cur:
        found_cust = Customer(
            row[1].strip(),
            f"{row[2].strip()} {row[3].strip()}",
            row[5],
            row[4].strip(),
        )
        results.append(found_cust)

    return results


def get_filtered_rentals(
    filter_attributes: Rental = None,
    min_rental_date: str = None,
    max_rental_date: str = None,
    min_due_date: str = None,
    max_due_date: str = None,
) -> list[Rental]:
    """
    Returns a list of Rental objects matching the filters.
    """
    where_clause = f"WHERE"
    where_clause_used = 0
    comp = "="
    if filter_attributes.item_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" item_id {comp} '{filter_attributes.item_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND item_id {comp} '{filter_attributes.item_id}'"
            )

    if filter_attributes.customer_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" customer_id {comp} '{filter_attributes.customer_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause
                + f" AND customer_id {comp} '{filter_attributes.customer_id}'"
            )

    if min_rental_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" rental_date >= '{min_rental_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND rental_date >= '{min_rental_date}'"

    if max_rental_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" rental_date <= '{max_rental_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND rental_date <= '{max_rental_date}'"

    if min_due_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" due_date >= '{min_due_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND due_date >= '{min_due_date}'"

    if max_due_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" due_date <= '{max_due_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND due_date <= '{max_due_date}'"

    query = f"SELECT * FROM Rental {where_clause};"
    cur.execute(query)

    results = []
    for row in cur:
        found_rental = Rental(
            row[0].strip(), row[1].strip(), row[2].isoformat(), row[3].isoformat()
        )
        results.append(found_rental)

    return results


def get_filtered_rental_histories(
    filter_attributes: RentalHistory = None,
    min_rental_date: str = None,
    max_rental_date: str = None,
    min_due_date: str = None,
    max_due_date: str = None,
    min_return_date: str = None,
    max_return_date: str = None,
) -> list[RentalHistory]:
    """
    Returns a list of RentalHistory objects matching the filters.
    """
    where_clause = f"WHERE"
    where_clause_used = 0
    comp = "="
    if filter_attributes.item_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" item_id {comp} '{filter_attributes.item_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND item_id {comp} '{filter_attributes.item_id}'"
            )

    if filter_attributes.customer_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" customer_id {comp} '{filter_attributes.customer_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause
                + f" AND customer_id {comp} '{filter_attributes.customer_id}'"
            )

    if min_rental_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" rental_date >= '{min_rental_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND rental_date >= '{min_rental_date}'"

    if max_rental_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" rental_date <= '{max_rental_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND rental_date <= '{max_rental_date}'"

    if min_due_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" due_date >= '{min_due_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND due_date >= '{min_due_date}'"

    if max_due_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" due_date <= '{max_due_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND due_date <= '{max_due_date}'"

    if min_return_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" return_date >= '{min_return_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND return_date >= '{min_return_date}'"

    if max_return_date is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" return_date <= '{max_return_date}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND return_date <= '{max_return_date}'"

    query = f"SELECT * FROM rental_history {where_clause};"
    cur.execute(query)

    results = []
    for row in cur:
        found_rental = RentalHistory(
            row[0].strip(),
            row[1].strip(),
            row[2].isoformat(),
            row[3].isoformat(),
            row[4].isoformat(),
        )
        results.append(found_rental)

    return results


def get_filtered_waitlist(
    filter_attributes: Waitlist = None,
    min_place_in_line: int = -1,
    max_place_in_line: int = -1,
) -> list[Waitlist]:
    """
    Returns a list of Waitlist objects matching the filters.
    """
    where_clause = f"WHERE"
    where_clause_used = 0
    comp = "="
    if filter_attributes.item_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" item_id {comp} '{filter_attributes.item_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause + f" AND item_id {comp} '{filter_attributes.item_id}'"
            )

    if filter_attributes.customer_id is not None:
        if where_clause_used == False:
            where_clause = (
                where_clause + f" customer_id {comp} '{filter_attributes.customer_id}'"
            )
            where_clause_used = True
        else:
            where_clause = (
                where_clause
                + f" AND customer_id {comp} '{filter_attributes.customer_id}'"
            )

    if min_place_in_line > 0:
        if where_clause_used == False:
            where_clause = where_clause + f" place_in_line >= '{min_place_in_line}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND place_in_line >= '{min_place_in_line}'"

    if max_place_in_line > 0:
        if where_clause_used == False:
            where_clause = where_clause + f" place_in_line <= '{max_place_in_line}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND place_in_line <= '{max_place_in_line}'"

    query = f"SELECT * FROM waitlist {where_clause};"
    cur.execute(query)

    results = []
    for row in cur:
        found_rental = Waitlist(row[0].strip(), row[1].strip(), row[2])
        results.append(found_rental)

    return results


def number_in_stock(item_id: str = None) -> int:
    """
    Returns num_owned - active rentals. Returns -1 if item doesn't exist.
    """

    num_owned_query = f"SELECT i_num_owned FROM item WHERE i_item_id = '{item_id}'"
    cur.execute(num_owned_query)
    row = cur.fetchone()
    if row is None or row[0] is None:
        return -1

    n_owned = row[0]

    num_rent_query = f"SELECT count(*) FROM rental WHERE item_id = '{item_id}'"
    cur.execute(num_rent_query)
    n_rented = cur.fetchone()[0]

    return n_owned - n_rented


def place_in_line(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's place_in_line, or -1 if not on waitlist.
    """
    where_clause = f"WHERE"
    where_clause_used = 0
    comp = "="
    if item_id is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" item_id {comp} '{item_id}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND item_id {comp} '{item_id}'"

    if customer_id is not None:
        if where_clause_used == False:
            where_clause = where_clause + f" customer_id {comp} '{customer_id}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND customer_id {comp} '{customer_id}'"

    query = f"SELECT place_in_line FROM waitlist {where_clause};"
    cur.execute(query)
    result = cur.fetchone()
    return result[0] if result and result[0] is not None else -1


def line_length(item_id: str = None) -> int:
    """
    Returns how many people are on the waitlist for this item.
    """
    query = f"SELECT COUNT(*) FROM waitlist WHERE item_id = '{item_id}'"
    cur.execute(query)
    return cur.fetchone()[0]


def save_changes():
    """
    Commits all changes made to the db.
    """
    conn.commit()


def close_connection():
    """
    Closes the cursor and connection.
    """
    conn.close()
