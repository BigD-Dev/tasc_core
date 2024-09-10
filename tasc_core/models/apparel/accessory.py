class Accessory:
    """
    The object represents a single accessory with detailed attributes such as type, color, material, etc.

    It contains methods to interact with the accessory item, including updating stock, applying discounts, and matching with other items.

    Attributes:
        item_id (str): Unique identifier for the accessory item.
        name (str): The name or title of the accessory item.
        type (str): The type of accessory, e.g., 'Belt', 'Hat', 'Jewelry'.
        color (str): The color of the accessory item.
        material (str): The material from which the accessory item is made.
        style (str): The style of the accessory item, e.g., 'Modern', 'Vintage'.
        brand (str): The brand of the accessory item.
        compatibility (str): The compatibility of the accessory, e.g., 'Universal', 'Specific outfits'.
        gender (str): The gender for which the accessory item is designed.
        price (float): The price of the accessory item.
        availability (int): The stock availability of the accessory item.

    Methods:
        display_info(): Display basic information about the accessory item.
        update_stock(new_stock): Update the stock availability for the item.
        apply_discount(discount_percentage): Apply a discount to the item.
        match_with(other_item): Check if the item can be matched with another accessory item.
    """

    def __init__(self, item_id, name, type, color, material, style, brand, compatibility, gender, price,
                 availability):
        super().__init__(item_id, name, 'Accessory', color, material, style, brand, gender, price, availability)
        self.type = type
        self.compatibility = compatibility