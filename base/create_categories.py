import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from capsule.models import Category, SubCategory

def create_categories():
    categories = {
        "Shirts": [
            "Casual shirts", "Business shirts", "Oxford shirts", "Denim Shirts", 
            "Corduroy shirts", "Checkered shirts", "Overshirts", "Short-sleeved shirts", 
            "Linen shirts", "Tuxedo shirts"
        ],
        "T-Shirts": [
            "Short-sleeved t-shirts", "V-neck t-shirts", "Long-sleeved t-shirts", 
            "Sleeveless shirts"
        ],
        "Polo Shirts": [
            "Short-sleeved polos", "Long-sleeved polos"
        ],
        "Shorts": [
            "Chinos shorts", "Cargo shorts", "Denim shorts", "Sweat shorts", 
            "Linen shorts"
        ],
        "Swimwear": [
            "Swim shorts", "Briefs"
        ],
        "Sweatshirts": [
            "Sweatshirts", "Hoodies", "Teddy sweaters", "Track jackets"
        ],
        "Jeans": [
            "Slim jeans", "Regular jeans", "Tapered jeans", "Loose jeans", 
            "Skinny jeans"
        ],
        "Knitwear": [
            "Round Necks", "V-necks", "Half zip jumpers", "Full zip jumpers", 
            "Turtlenecks", "Cardigans", "Knitted polos", "Knitted vests"
        ],
        "Trousers": [
            "Chinos", "Business Trousers", "Casual trousers", "Cargo pants", 
            "Linen trousers"
        ],
        "Overshirts": [],
        "Suits & Blazers": [
            "Suits", "Blazers", "Waistcoats", "Tuxedos"
        ],
        "Sweatpants": [],
        "Rainwear": [
            "Rain coats", "Waterproof trousers", "Rain boots"
        ],
        "Outerwear": [
            "Jackets", "Coats", "Vests"
        ]
    }

    for category_name, subcategories in categories.items():
        category, created = Category.objects.get_or_create(name=category_name)
        for subcategory_name in subcategories:
            SubCategory.objects.get_or_create(name=subcategory_name, category=category)

if __name__ == "__main__":
    create_categories()
    print("Categories and subcategories created successfully!")