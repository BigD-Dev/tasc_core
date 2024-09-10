class Clothing(Apparel):
    """
    The object represents a single piece of clothing, with detailed attributes such as size, color, material, etc.

    It contains methods to interact with the clothing item, including updating stock, applying discounts, and matching with other items.

    Examples:
        Here is how you might use the Clothing object:

            # Create a new clothing item
            shirt = Clothing(
                item_id='S123',
                name='Casual Shirt',
                category='Shirt',
                size='M',
                color='Blue',
                material='Cotton',
                style='Casual',
                brand='FashionBrand',
                season='Summer',
                gender='Unisex',
                price=29.99,
                availability=10
            )

            # Display information about the clothing item
            shirt.display_info()

            # Update the stock for the item
            shirt.update_stock(20)

            # Apply a discount to the item
            shirt.apply_discount(15)

            # Assuming we have another item 'pants', check if they match
            shirt.match_with(pants)

    Attributes:
        item_id (str): Unique identifier for the clothing item.
        name (str): The name or title of the clothing item.
        category (str): The category this item belongs to e.g., 'Shirt', 'Pants'.
        size (str): The size of the clothing item.
        color (str): The color of the clothing item.
        material (str): The material from which the clothing item is made.
        style (str): The style of the clothing item e.g., 'Casual', 'Formal'.
        brand (str): The brand of the clothing item.
        season (str): The season for which the clothing item is suited.
        gender (str): The gender for which the clothing item is designed.
        price (float): The price of the clothing item.
        availability (int): The stock availability of the clothing item.

    """

    def __init__(self, item_id, name, size, color, material, style, brand, season, gender, price, availability):
        super().__init__(item_id, name, 'Clothing', color, material, style, brand, gender, price, availability)
        self.size = size
        self.season = season

    def display_info(self):
        # Display basic information about the clothing item
        info = (
            f"Item ID: {self.item_id}\n"
            f"Product ID: {self.product_id}\n"
            f"Name: {self.name}\n"
            f"Category: {self.category}\n"
            f"Size: {self.size}\n"
            f"Color: {self.color}\n"
            f"Material: {self.material}\n"
            f"Style: {self.style}\n"
            f"Brand: {self.brand}\n"
            f"Season: {self.season}\n"
            f"Gender: {self.gender}\n"
            f"Price: ${self.price}\n"
            f"Available: {self.availability}"
        )
        print(info)

    def update_stock(self, new_stock):
        # Update the stock availability for the item
        self.availability = new_stock
        print(f"Stock updated to {self.availability}")

    def apply_discount(self, discount_percentage):
        # Apply a discount to the item
        self.price -= (self.price * discount_percentage / 100)
        print(f"Discount applied. New price: ${self.price}")

    def match_with(self, other_item):
        # Check if the item can be matched with another clothing item
        if self.category != other_item.category and self.gender == other_item.gender:
            print(f"{self.name} can be matched with {other_item.name}.")
        else:````
            print(f"{self.name} cannot be matched with {other_item.name}.")