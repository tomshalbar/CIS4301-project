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

    insert_query = f"INSERT INTO item(i_item_sk, i_item_id, i_rec_start_date, i_product_name, i_brand, i_category, i_manufact, i_current_price, i_num_owned) VALUES ({new_item_sk}, {new_item.item_id}, {new_item_rec_start_date}, {new_item.product_name}, {new_item.brand}, {new_item.category}, {new_item.manufact}, {new_item.current_price}, {new_item.num_owned})"

    cur.execute(insert_query)


def add_customer(new_customer: Customer = None):
    """
    new_customer - A Customer object containing a new customer to be inserted into the DB in the customer table.
        new_customer and its attributes will never be None.
    """
    raise NotImplementedError("you must implement this function")


def edit_customer(original_customer_id: str = None, new_customer: Customer = None):
    """
    original_customer_id - A string containing the customer id for the customer to be edited.
    new_customer - A Customer object containing attributes to update. If an attribute is None, it should not be altered.
    """
    raise NotImplementedError("you must implement this function")


def rent_item(item_id: str = None, customer_id: str = None):
    """
    item_id - A string containing the Item ID for the item being rented.
    customer_id - A string containing the customer id of the customer renting the item.
    """
    raise NotImplementedError("you must implement this function")


def waitlist_customer(item_id: str = None, customer_id: str = None) -> int:
    """
    Returns the customer's new place in line.
    """
    raise NotImplementedError("you must implement this function")


def update_waitlist(item_id: str = None):
    """
    Removes person at position 1 and shifts everyone else down by 1.
    """
    raise NotImplementedError("you must implement this function")


def return_item(item_id: str = None, customer_id: str = None):
    """
    Moves a rental from rental to rental_history with return_date = today.
    """
    raise NotImplementedError("you must implement this function")


def grant_extension(item_id: str = None, customer_id: str = None):
    """
    Adds 14 days to the due_date.
    """
    raise NotImplementedError("you must implement this function")


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
            item_id=row[1],
            product_name=row[3],
            brand=row[4],
            category=row[6],
            manufact=row[7],
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
        found_cust = Customer(row[1], f"{row[2]} {row[3]}", row[5], row[4])
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
        found_rental = Rental(row[0], row[1], row[2], row[3])
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
        found_rental = RentalHistory(row[0], row[1], row[2], row[3], row[4])
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
            where_clause = where_clause + f" AND return_date >= '{min_place_in_line}'"

    if max_place_in_line > 0:
        if where_clause_used == False:
            where_clause = where_clause + f" place_in_line <= '{max_place_in_line}'"
            where_clause_used = True
        else:
            where_clause = where_clause + f" AND return_date <= '{max_place_in_line}'"

    query = f"SELECT * FROM waitlist {where_clause};"
    cur.execute(query)

    results = []
    for row in cur:
        found_rental = Waitlist(row[0], row[1], row[2])
        results.append(found_rental)

    return results


def number_in_stock(item_id: str = None) -> int:
    """
    Returns num_owned - active rentals. Returns -1 if item doesn't exist.
    """

    num_owned_query = f"SELECT i_num_owned FROM item WHERE i_item_id = '{item_id}'"
    cur.execute(num_owned_query)
    n_owned = cur.fetchone()[0]

    num_rent_query = f"SELECT count(*) FROM rental WHERE item_id = '{item_id}'"
    cur.execute(num_rent_query)
    n_rented = cur.fetchone()[0]

    return n_owned - n_rented


print(number_in_stock("AAAAAAAABAAAAAAA"))


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
    return cur.fetchone()[0]


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
