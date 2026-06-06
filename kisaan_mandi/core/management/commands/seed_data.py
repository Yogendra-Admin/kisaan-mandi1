from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from marketplace.models import Category, Product
from prices.models import MarketPrice
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed demo data with English, Hindi and Nepali content'

    def handle(self, *args, **kwargs):
        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@kisaanmandi.in', 'admin123', role='admin', first_name='Admin')
            self.stdout.write('Created admin (admin/admin123)')

        # Farmers
        farmers_data = [
            ('ramu_farmer', 'Ramu', 'Sharma', 'Maharashtra', 'Nashik', '9876543210'),
            ('priya_kisan', 'Priya', 'Patel', 'Gujarat', 'Anand', '9876543211'),
            ('suresh_farm', 'Suresh', 'Kumar', 'Punjab', 'Ludhiana', '9876543212'),
            ('ram_bahadur', 'Ram Bahadur', 'Thapa', 'Bagmati', 'Kathmandu', '9841234567'),
        ]
        farmers = []
        for uname, fn, ln, state, dist, phone in farmers_data:
            u, created = User.objects.get_or_create(username=uname, defaults={
                'first_name': fn, 'last_name': ln, 'role': 'farmer',
                'state': state, 'district': dist, 'phone': phone,
                'email': f'{uname}@example.com'
            })
            if created:
                u.set_password('farmer123')
                u.save()
            farmers.append(u)

        # Buyer
        if not User.objects.filter(username='demo_buyer').exists():
            b = User.objects.create_user('demo_buyer', 'buyer@example.com', 'buyer123',
                role='buyer', first_name='Demo', last_name='Buyer', state='Delhi')
            b.save()

        # Categories with Nepali
        cats = [
            ('Grains',      'अनाज',     'अन्न',     '🌾', 'grains'),
            ('Vegetables',  'सब्जियाँ', 'तरकारी',   '🥦', 'vegetables'),
            ('Fruits',      'फल',       'फलफूल',    '🍎', 'fruits'),
            ('Spices',      'मसाले',    'मसला',     '🌶', 'spices'),
            ('Pulses',      'दालें',    'दाल',      '🫘', 'pulses'),
            ('Dairy',       'डेयरी',    'दुग्ध',    '🥛', 'dairy'),
            ('Oilseeds',    'तिलहन',    'तेलबीज',   '🌻', 'oilseeds'),
        ]
        cat_objs = {}
        for name, name_hi, name_ne, icon, slug in cats:
            c, _ = Category.objects.get_or_create(slug=slug, defaults={
                'name': name, 'name_hi': name_hi, 'name_ne': name_ne, 'icon': icon
            })
            # Update Nepali if already exists
            if not c.name_ne:
                c.name_ne = name_ne; c.save()
            cat_objs[slug] = c

        # Products with Nepali names
        products_data = [
            (farmers[0], 'Onion',        'प्याज',          'प्याज',          cat_objs['vegetables'], 25.00,  'kg',      500, 'Nashik',    'Maharashtra', False),
            (farmers[0], 'Tomato',       'टमाटर',          'गोलभेडा',        cat_objs['vegetables'], 18.50,  'kg',      300, 'Nashik',    'Maharashtra', True),
            (farmers[1], 'Wheat',        'गेहूँ',          'गहुँ',           cat_objs['grains'],     2200,   'quintal',  50, 'Anand',     'Gujarat',     False),
            (farmers[1], 'Turmeric',     'हल्दी',          'बेसार',          cat_objs['spices'],     120,    'kg',      100, 'Anand',     'Gujarat',     True),
            (farmers[2], 'Basmati Rice', 'बासमती चावल',   'बासमती चामल',   cat_objs['grains'],     4500,   'quintal',  20, 'Ludhiana',  'Punjab',      False),
            (farmers[2], 'Moong Dal',    'मूंग दाल',       'मुसुरो दाल',    cat_objs['pulses'],     95,     'kg',      200, 'Ludhiana',  'Punjab',      True),
            (farmers[0], 'Potato',       'आलू',            'आलु',            cat_objs['vegetables'], 15,     'kg',      800, 'Nashik',    'Maharashtra', False),
            (farmers[3], 'Mustard',      'सरसों',          'तोरी',           cat_objs['oilseeds'],   85,     'kg',      120, 'Kathmandu', 'Bagmati',     True),
            (farmers[3], 'Garlic',       'लहसुन',          'लसुन',           cat_objs['spices'],     150,    'kg',       80, 'Kathmandu', 'Bagmati',     False),
        ]
        for farmer, name, name_hi, name_ne, cat, price, unit, qty, loc, state, organic in products_data:
            p, created = Product.objects.get_or_create(name=name, farmer=farmer, defaults={
                'name_hi': name_hi, 'name_ne': name_ne, 'category': cat,
                'price_per_unit': price, 'unit': unit, 'quantity_available': qty,
                'location': loc, 'state': state, 'is_organic': organic, 'status': 'active'
            })
            if not created and not p.name_ne:
                p.name_ne = name_ne; p.save()

        # Market prices with Nepali crop names
        prices = [
            ('Wheat',    'गेहूँ',    'गहुँ',     'Azadpur Mandi',    'Delhi',        1900, 2100, 2050, 'Quintal', 'up'),
            ('Rice',     'चावल',    'चामल',     'Patna Mandi',      'Bihar',        3200, 3800, 3500, 'Quintal', 'stable'),
            ('Onion',    'प्याज',   'प्याज',    'Lasalgaon Mandi',  'Maharashtra',   800, 1200, 1050, 'Quintal', 'down'),
            ('Potato',   'आलू',     'आलु',      'Agra Mandi',       'Uttar Pradesh', 600,  900,  750, 'Quintal', 'stable'),
            ('Tomato',   'टमाटर',   'गोलभेडा',  'Kolar Mandi',      'Karnataka',     400,  800,  600, 'Quintal', 'up'),
            ('Turmeric', 'हल्दी',   'बेसार',    'Erode Mandi',      'Tamil Nadu',   7000, 9000, 8200, 'Quintal', 'up'),
            ('Mustard',  'सरसों',   'तोरी',     'Asan Tol Bazar',   'Bagmati',      6000, 7500, 6800, 'Quintal', 'stable'),
            ('Garlic',   'लहसुन',   'लसुन',     'Kalimati Bazar',   'Bagmati',     12000,15000,13500, 'Quintal', 'up'),
        ]
        for name, name_hi, name_ne, mandi, state, minp, maxp, modal, unit, trend in prices:
            mp, created = MarketPrice.objects.get_or_create(
                crop_name=name, mandi_name=mandi, date=date.today(),
                defaults={'crop_name_hi': name_hi, 'crop_name_ne': name_ne, 'state': state,
                          'min_price': minp, 'max_price': maxp, 'modal_price': modal,
                          'unit': unit, 'trend': trend}
            )
            if not created and not mp.crop_name_ne:
                mp.crop_name_ne = name_ne; mp.save()

        self.stdout.write(self.style.SUCCESS('[SUCCESS] Demo data seeded successfully!'))
        self.stdout.write('   Admin:   admin / admin123')
        self.stdout.write('   Farmer:  ramu_farmer / farmer123')
        self.stdout.write('   Farmer:  ram_bahadur / farmer123  (Nepali)')
        self.stdout.write('   Buyer:   demo_buyer / buyer123')
