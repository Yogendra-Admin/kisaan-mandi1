import os
import sys
import django

# Setup django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kisaan_mandi.settings')
django.setup()

from marketplace.models import Product, Category
from accounts.models import CustomUser

def check_products():
    products = Product.objects.all()
    print(f"Total products in database: {products.count()}")
    
    errors = []
    for p in products:
        p_errors = []
        if not p.name:
            p_errors.append("Missing English name")
        if not p.name_hi:
            p_errors.append("Missing Hindi name (name_hi)")
        if not p.name_ne:
            p_errors.append("Missing Nepali name (name_ne)")
        if p.price_per_unit <= 0:
            p_errors.append(f"Invalid price: {p.price_per_unit}")
        if p.quantity_available < 0:
            p_errors.append(f"Invalid quantity: {p.quantity_available}")
        if not p.farmer:
            p_errors.append("Missing farmer relationship")
        elif p.farmer.role != 'farmer':
            p_errors.append(f"Farmer '{p.farmer.username}' has invalid role: {p.farmer.role}")
        if not p.category:
            p_errors.append("Missing category relationship")
        if not p.location:
            p_errors.append("Missing location")
        if not p.state:
            p_errors.append("Missing state")
            
        if p_errors:
            errors.append(f"Product #{p.id} ({p.name}): " + ", ".join(p_errors))
            
    if errors:
        print("\nFound issues in products:")
        for err in errors:
            print(f"- {err}")
    else:
        print("\nAll existing products are correct and complete!")

if __name__ == "__main__":
    check_products()
