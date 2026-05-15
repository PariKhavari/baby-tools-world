from django.core.management.base import BaseCommand

from products.models import Category, Product

categories_list = [("boys", "", "boys"), ("girls", "", "girls"), ("toys", "", "toys"), ("outdoor", "", "outdoor")]
products = [
    {
        "category": "boys",
        "description": "",
        "name": "jumpsuit-blue-01",
        "price": 9.99,
        "image": "imgs/products/jumpsuit-blue.jpeg",
    },
    {
        "category": "boys",
        "description": "",
        "name": "pacifier-blue",
        "price": 1.99,
        "image": "imgs/products/blue-pacifier.jpeg",
    },
    {
        "category": "boys",
        "description": "",
        "name": "wooden-sword-sir-babylot",
        "price": 22.99,
        "image": "imgs/products/wooden-sword.png",
    },
    {
        "category": "girls",
        "description": "",
        "name": "jumpsuit-pink-01",
        "price": 9.99,
        "image": "imgs/products/jumpsuit-rosa.jpeg",
    },
    {
        "category": "girls",
        "description": "",
        "name": "pacifier-pink",
        "price": 1.99,
        "image": "imgs/products/rosa-pacifier.jpeg",
    },
    {
        "category": "girls",
        "description": "",
        "name": "cuddly-dolphin",
        "price": 17.49,
        "image": "imgs/products/cuddly-dolphin.png",
    },
    {
        "category": "toys",
        "description": "",
        "name": "kids-kitchen-le-chef",
        "price": 45.99,
        "image": "imgs/products/blue-kitchen.png",
    },
    {
        "category": "toys",
        "description": "",
        "name": "kids-kitchen-le-bakery (rosa)",
        "price": 49.99,
        "image": "imgs/products/rosa-kitchen.png",
    },
    {
        "category": "toys",
        "description": "",
        "name": "soft-ball",
        "price": 10.00,
        "image": "imgs/products/baby-ball.png",
    },
    {
        "category": "toys",
        "description": "",
        "name": "rattle-blue",
        "price": 11.00,
        "image": "imgs/products/blue-rattle.png",
    },
    {
        "category": "toys",
        "description": "",
        "name": "rattle-rosa",
        "price": 11.00,
        "image": "imgs/products/rosa-rattle.png",
    },
    {
        "category": "toys",
        "description": "",
        "name": "wooden-horse",
        "price": 22.98,
        "image": "imgs/products/wooden-horse.png",
    },
    {
        "category": "outdoor",
        "description": "",
        "name": "sun-cream-baby-strong",
        "price": 0.99,
        "image": "imgs/products/baby-suncream.png",
    },
    {
        "category": "outdoor",
        "description": "",
        "name": "sun-hat",
        "price": 4.99,
        "image": "imgs/products/baby-sunhat.png",
    },
    {
        "category": "outdoor",
        "description": "",
        "name": "baby-bottle",
        "price": 8.99,
        "image": "imgs/products/baby-bottle.png",
    },
]


class Command(BaseCommand):
    help = "Seeds the database with initial category and product data"

    def handle(self, *args, **kwargs):
        # TODO: create and add categories and product data
        self.stdout.write(self.style.SUCCESS("Beginning to seed the database..."))

        created_categories = 0

        # Create categories
        try:
            for category in categories_list:
                # Check if category already exists
                if Category.objects.filter(name=category[0]).exists():
                    self.stdout.write(
                        self.style.WARNING(f"Category '{category[0]}' already exists. Skipping creation.")
                    )
                    continue
                # Create a new category
                category = Category.objects.create(name=category[0], description=category[1], slug=category[2])
                created_categories += 1
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
        except Exception as err:
            self.stdout.write(self.style.ERROR(f"Error creating category: {err}"))

        self.stdout.write(self.style.SUCCESS(f"{created_categories} Categories created successfully."))

        # Create products
        created_products = 0

        try:
            for product in products:
                # Get the category object, if non-existent abort seeding
                category = Category.objects.filter(name=product["category"]).first()
                if not category:
                    self.stdout.write(
                        self.style.ERROR(f"Category '{product['category']}' does not exist. Skipping product creation.")
                    )
                    continue

                # Check if product already exists
                if Product.objects.filter(name=product["name"]).exists():
                    self.stdout.write(
                        self.style.WARNING(f"Product '{product['name']}' already exists. Skipping creation.")
                    )
                    continue

                # Create a new product
                new_product = Product.objects.create(
                    category=category,
                    description=product["description"],
                    name=product["name"],
                    price=product["price"],
                    image=product["image"],
                )
                created_products += 1
                self.stdout.write(self.style.SUCCESS(f"Created product: {new_product.name}"))

            self.stdout.write(self.style.SUCCESS(f"{created_products} Products created successfully."))

        except Exception as err:
            self.stdout.write(self.style.ERROR(f"Error creating products: {err}"))
