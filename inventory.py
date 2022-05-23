""" This program reads and outputs the data found in inventory.txt
    in a simple-to-read format.
"""
from __future__ import annotations
from os import path
from typing import List, Dict, Optional, Union
from tabulate import tabulate

Shoe_Dict = Dict[str, Union[int,float,str]]
# Allow the program to be run correctly from any working directory
inventory_txt = 'inventory.txt'
inventory_path = path.join(path.dirname(__file__), inventory_txt)


class Shoe(object):
    """
    A class to represent a shoe.
    ...
    Attributes
    ----------
    country: str    The shoe's country of origin.
    code: str       The shoe's SKU code.
    product: str    The shoe's product name.
    cost: int       The cost of the shoe.
    quantity: int   The quantity of the shoe in stock.

    """
    country: str
    code: str
    product: str
    cost: Union[int,float]
    quantity: int

    def __init__(
            self, details: List[str]
    ):
        self.country = details[0]
        self.code = details[1]
        self.product = details[2]
        self.cost = int(details[3])
        self.quantity = int(details[4])

    def get_cost(self):
        # This function gets the cost of a Shoe instance
        return self.cost

    def get_quantity(self):
        # This function is used to get the quantity of a Shoe instance
        return self.quantity

    def dict(self):
        return {
            "Country": self.country,
            "Code": self.code,
            "Product": self.product,
            "Cost": self.cost,
            "Quantity": self.quantity,
        }

    def __str__(self):
        """ This method converts an instance of Shoe into a string
            which is properly formatted for inventory.txt
        """
        value_list = self.dict().values()
        return ','.join(str(val) for val in value_list)


shoes: List[Shoe] = []


def read_shoes_data():
    try:
        shoes.clear()
        with open(inventory_path, 'r') as inventory:
            shoe_list: List[List[str]] = []
            count = 0
            for line in inventory:
                if count > 0:
                    curr_shoe = line.strip().split(',')
                    shoe_list.append(curr_shoe)

                count += 1

            if len(shoe_list) == 1:
                raise Exception(f"{inventory_txt} is empty!")
            elif len(shoe_list) == 0:
                raise Exception(f"There are no products in {inventory_txt}")

            capture_shoes(shoe_list)

    except OSError as error:
        print(error)
        raise Exception("Something went wrong while reading inventory.txt")


def capture_shoes(shoe_list: List[List[str]]):
    """This function creates a list of Shoe objects from a list of lists.
    Used https://stackoverflow.com/questions/6360286 to get around logical
    error where .append() filled `shoes` with the most current item.
    (assigning list[:] copies all values to a new list)"""
    for line, shoe in enumerate(shoe_list[:]):
        if len(shoe) != 5:
            raise Exception(f"{inventory_txt} is not in the correct format.")
        try:
            shoes.append(Shoe(shoe))
        except ValueError:
            print(f"Shoe data at line {line + 1} is malformed.")


def view_all():
    """This function creates a neat table of the data in inventory.txt
    """
    shoe_list = shoes[:]  # Copy the values in `shoes[]`
    shoe_details: List[Dict[str, Union[int,float,str]]] = []

    for shoe in shoe_list:
        shoe_details.append(shoe.dict())
    print(
        tabulate(
            shoe_details, headers="keys"
        )
    )


def positive_int(value: Union[str,int]) -> int:
    """This function forces the user to enter a positive number"""
    new_value = int(value)
    if new_value < 0:
        raise Exception("Only a positive number is allowed here")
    return new_value


def re_stock():
    """ This function determines the shoe with the lowest quantity
        and asks the user if they wish to restock it.
    """
    lowest_index = 0
    shoes_ref = shoes[:]  # Copy the values in `shoes[]`
    for s, shoe in enumerate(shoes_ref):
        if shoe.get_quantity() < shoes_ref[lowest_index].get_quantity():
            lowest_index = s

    shoe_with_lowest = shoes_ref[lowest_index]
    # Inform the user of the product with low stock (and its quantity)
    display_shoe(shoe_with_lowest, "Product with lowest quantity: ")
    # Add a new quantity to current stock
    shoes_ref[lowest_index].quantity += positive_int(
        input("How many shoes should be added to the current stock? ")
    )
    print("Item updated: ")
    display_shoe(shoe_with_lowest, "Item updated: ")
    with open(inventory_path, 'r') as inventory:
        new_inv: List[str] = []
        # Start at -1 as the header line is not in the shoes list.
        for line, data in enumerate(inventory, start=-1):
            if line != lowest_index:
                new_inv.append(data.strip())
                continue
            else:
                new_inv.append(shoe_with_lowest.__str__())

    with open(inventory_path, 'w') as inventory:
        inventory.write('\n'.join(new_inv))
    read_shoes_data()


def search_shoe():
    """This function searches for a shoe with an SKU matching the SKU provided."""
    code: str = input("SKU: ").strip()
    for shoe in shoes:
        if shoe.code == code:
            display_shoe(shoe, "Product found:")
            # Get out of the function
            return
    print("No items with the SKU provided were found.")


def value_per_item():
    """ This function assigns a value to each item in shoes using the formula:
        value = cost * quantity
    """
    shoe_data: List[Shoe] = shoes[:]
    new_data: List[Shoe_Dict] = []
    for _, shoe in enumerate(shoe_data):
        curr_shoe = shoe.dict()
        curr_shoe["Value"] = shoe.get_cost() * shoe.get_quantity()
        new_data.append(curr_shoe)
    print(tabulate(new_data, headers="keys"))


def highest_qty():
    """ This function determines the item with the highest quantity
        and puts it on sale according to a given percentage.
    """
    shoes_ref = shoes[:]
    index_of_highest = 0
    highest_qty = 0

    for s, shoe in enumerate(shoes_ref):
        if shoe.get_quantity() > highest_qty:
            index_of_highest = s
            highest_qty = shoe.get_quantity()

    # Select the shoe with the highest quantity
    highest_qty_shoe = shoes[index_of_highest]
    display_shoe(highest_qty_shoe)

    discount_percent: int = positive_int(
        input("Discount percentage: ")
    )
    # H * 1 - H * {discount}% = price with discount.
    highest_qty_shoe.cost *= +(1 - discount_percent / 100)
    display_shoe(highest_qty_shoe, f"{discount_percent}% sale: ")


item_template = '''
=====================
Product:    {Product}
Price:      R{Cost:.2f}
Country:    {Country}
Quantity:   {Quantity}
Code:       {Code}
=====================\
'''


def display_shoe(shoe: Shoe, message: Optional[str] = None):
    """This function displays the details of a single shoe."""
    # Format string with dict: https://stackoverflow.com/questions/5952344
    curr_shoe = shoe.dict()
    if message:
        print(message)
    print(item_template.format_map(curr_shoe))


instruction_dict = {
    'a': view_all,
    'r': re_stock,
    's': search_shoe,
    'h': highest_qty,
    'v': value_per_item,
    'e': exit
}

instructions = '''
What would you like to do?
a - View all shoes
r - Restock shoe with lowest quantity
s - Search shoe by SKU
h - Find shoe with highest quantity
v - Assign a value to each item
e - Exit the program'''

# Read inventory.txt contents to memory before the program starts.
read_shoes_data()


while True:
    print(instructions)
    option = input(": ")

    if option in instruction_dict:
        instruction_dict[option]()
    else:
        print("Incorrect option provided.")
