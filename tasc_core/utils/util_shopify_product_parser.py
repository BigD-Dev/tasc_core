import json
import requests
import pandas as pd
from requests.exceptions import HTTPError

class ShopifyProductParser:
    def __init__(self, url: str):
        """
        Initialize the ShopifyProductParser with a URL to JSON data.

        Args:
            url (str): URL to the JSON data.
        """
        self.url = url
        self.json_data = None
        self.parsed_data = None

    def load_json(self):
        """
        Load JSON data from a URL.

        Raises:
            ValueError: If the JSON data is not valid or the response is empty.
            HTTPError: If there is an HTTP error during the request.

        Example:
            parser = ShopifyProductParser(url)
            parser.load_json()
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except HTTPError as http_err:
            raise HTTPError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise Exception(f"An error occurred: {err}")

        if not response.content:
            raise ValueError("Empty response from the URL")

        try:
            self.json_data = response.json()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")

    def parse_products(self):
        """
        Parse the JSON data into a list of dictionaries capturing all fields.

        Returns:
            list: A list of dictionaries with product and variant details.

        Raises:
            ValueError: If JSON data is not loaded.

        Example:
            parser = ShopifyProductParser(url)
            parser.load_json()
            products = parser.parse_products()
        """
        if self.json_data is None:
            raise ValueError("JSON data not loaded. Call load_json() first.")

        complete_products = []
        for product in self.json_data['products']:
            # Extract up to 5 image URLs
            images = product.get('images', [])
            image_urls = [img['src'] for img in images[:5]]
            image_fields = {f'product_image_{i + 1}_url': image_urls[i] if i < len(image_urls) else None for i in range(5)}

            # Extract sizes
            sizes = []
            for option in product.get('options', []):
                if option['name'].lower() == 'size':
                    sizes = option['values']
                    break

            for variant in product['variants']:
                complete_products.append({
                    'parent_product_id': product['id'],  # Add parent_product_id
                    'child_product_id': variant['id'],  # Add child_product_id
                    'product_title': product['title'],
                    'product_desc': product.get('body_html'),
                    'handle': product.get('handle'),
                    'vendor': product.get('vendor'),
                    'product_type': product.get('product_type'),
                    'tags': ", ".join(product.get('tags', [])),
                    'published_at': product.get('published_at'),
                    'created_at': product.get('created_at'),
                    'updated_at': product.get('updated_at'),
                    'variant_title': variant['title'],
                    'sku': variant.get('sku'),
                    'price': variant['price'],
                    'grams': variant['grams'],
                    'available': variant['available'],
                    'requires_shipping': variant['requires_shipping'],
                    'taxable': variant['taxable'],
                    'featured_image': variant.get('featured_image'),
                    'position': variant['position'],
                    'sizes': ", ".join(sizes),  # Add sizes field
                    **image_fields  # Add image fields to the dictionary
                })
        return complete_products

    def to_dataframe(self):
        """
        Convert the parsed product data to a DataFrame.

        Returns:
            DataFrame: A pandas DataFrame containing the product and variant details.

        Example:
            parser = ShopifyProductParser(url)
            parser.load_json()
            df = parser.to_dataframe()
        """
        complete_products = self.parse_products()
        return pd.DataFrame(complete_products)