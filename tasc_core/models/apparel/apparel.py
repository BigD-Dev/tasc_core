class Apparel:
    """
    The base class for all apparel items, including clothing, footwear, and accessories.
    This class defines common attributes and methods that can be inherited.
    """

    def __init__(self, item_id, product_id, name, apparel_type, colour, material, style, brand, gender, price, availability):
        self.item_id = item_id
        self.product_id = product_id
        self.name = name
        self.apparel_type = apparel_type
        self.colour = colour
        self.material = material
        self.style = style
        self.brand = brand
        self.gender = gender
        self.price = price
        self.availability = availability

    def display_info(self):
        info = (
            f"Item ID: {self.item_id}\n"
            f"Name: {self.name}\n"
            f"Category: {self.apparel_type}\n"
            f"Color: {self.colour}\n"
            f"Material: {self.material}\n"
            f"Style: {self.style}\n"
            f"Brand: {self.brand}\n"
            f"Gender: {self.gender}\n"
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

# Now, the Clothing, Footwear, and Accessory classes will inherit from Apparel:
