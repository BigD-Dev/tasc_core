class Footwear:
    """
    The object represents a single piece of footwear with detailed attributes such as size, color, material, etc.

    It contains methods to interact with the footwear item, including updating stock, applying discounts, and matching with other items.

    Attributes:
        item_id (str): Unique identifier for the footwear item.
        name (str): The name or title of the footwear item.
        type (str): The type of footwear, e.g., 'Boots', 'Sneakers', 'Heels'.
        size (str): The size of the footwear item.
        color (str): The color of the footwear item.
        material (str): The material from which the footwear item is made.
        style (str): The style of the footwear item, e.g., 'Casual', 'Athletic'.
        brand (str): The brand of the footwear item.
        season (str): The season for which the footwear item is suited.
        gender (str): The gender for which the footwear item is designed.
        price (float): The price of the footwear item.
        availability (int): The stock availability of the footwear item.
        fit (str): The fit of the footwear, e.g., 'Regular', 'Narrow', 'Wide'.

    Methods:
        display_info(): Display basic information about the footwear item.
        update_stock(new_stock): Update the stock availability for the item.
        apply_discount(discount_percentage): Apply a discount to the item.
        match_with(other_item): Check if the item can be matched with another footwear item.
    """
    def __init__(self, item_id, name, size, color, material, style, brand, fit, gender, price, availability):
        super().__init__(item_id, name, 'Footwear', color, material, style, brand, gender, price, availability)
        self.size = size
        self.fit = fit

    def display_info(self):
        info = (
            f"Item ID: {self.item_id}\n"
            f"Name: {self.name}\n"
            f"Type: {self.type}\n"
            f"Size: {self.size}\n"
            f"Color: {self.color}\n"
            f"Material: {self.material}\n"
            f"Style: {self.style}\n"
            f"Brand: {self.brand}\n"
            f"Season: {self.season}\n"
            f"Gender: {self.gender}\n"
            f"Fit: {self.fit}\n"
            f"Price: ${self.price}\n"
            f"Available: {self.availability}"
        )
        print(info)

    def update_stock(self, new_stock):
        self.availability = new_stock
        print(f"Stock updated to {self.availability}")

    def apply_discount(self, discount_percentage):
        self.price -= (self.price * discount_percentage / 100)
        print(f"Discount applied. New price: ${self.price}")

    def match_with(self, other_item):
        if self.type != other_item.type and self.gender == other_item.gender:
            print(f"{self.name} can be matched with {other_item.name}.")
        else:
            print(f"{self.name} cannot be matched with {other_item.name}.")