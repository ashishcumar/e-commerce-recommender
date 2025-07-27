# ecommerce_api/management/commands/load_products.py

import json
from django.core.management.base import BaseCommand, CommandError
from ecommerce_api.models import Product
import os

class Command(BaseCommand):
    help = 'Loads products from a JSON file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, nargs='?', default='products_data.json',
                            help='The name of the JSON file containing product data within the ecommerce_api app directory.')

    def handle(self, *args, **options):
        json_file_name = options['json_file']

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ecommerce_api_dir = os.path.dirname(os.path.dirname(current_dir))
        abs_json_file_path = os.path.join(ecommerce_api_dir, json_file_name)

        if not os.path.exists(abs_json_file_path):
            raise CommandError(f'File "{abs_json_file_path}" does not exist. Please ensure products_data.json is in the ecommerce_api directory.')

        self.stdout.write(self.style.SUCCESS(f'Attempting to load data from: {abs_json_file_path}'))

        try:
            with open(abs_json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                products_data = data.get('products', [])

        except json.JSONDecodeError:
            raise CommandError('Invalid JSON format in the file.')
        except Exception as e:
            raise CommandError(f'Error reading file: {e}')

        if not products_data:
            self.stdout.write(self.style.WARNING('No products found in the JSON file. Aborting.'))
            return

        products_created = 0
        for product_item in products_data:
            attributes_dict = {
                "brand": product_item.get("brand"),
                "tags": product_item.get("tags")
            }
            if 'dimensions' in product_item:
                attributes_dict['dimensions'] = product_item['dimensions']
            if 'weight' in product_item:
                attributes_dict['weight'] = product_item['weight']
            
            # Remove None values from attributes dictionary before serialization
            attributes_dict = {k: v for k, v in attributes_dict.items() if v is not None}
            
            # Convert the attributes dictionary to a JSON string
            attributes_json_string = json.dumps(attributes_dict)

            try:
                product, created = Product.objects.update_or_create(
                    name=product_item['title'],
                    defaults={
                        'description': product_item.get('description', ''),
                        'category': product_item.get('category', 'Uncategorized'),
                        'price': product_item.get('price', 0.00),
                        'stock_quantity': product_item.get('stock', 0),
                        'image_url': product_item.get('thumbnail', ''),
                        'attributes': attributes_json_string # Save as JSON string
                    }
                )
                if created:
                    products_created += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully created product: {product.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated product: {product.name}'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating/updating product {product_item.get("title", "N/A")}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Finished loading products. Total products created/updated: {len(products_data)}'))