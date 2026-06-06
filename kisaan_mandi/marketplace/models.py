from django.db import models
from accounts.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)
    name_hi = models.CharField(max_length=100, blank=True)
    name_ne = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=50, default='🌾')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        from .translation import translate_text
        if self.name:
            self.name_hi = translate_text(self.name, 'hi')
            self.name_ne = translate_text(self.name, 'ne')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    UNIT_CHOICES = [('kg', 'KG'), ('quintal', 'Quintal'), ('ton', 'Ton'), ('dozen', 'Dozen'), ('piece', 'Piece')]
    STATUS_CHOICES = [('active', 'Active'), ('sold', 'Sold'), ('inactive', 'Inactive')]

    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    name_hi = models.CharField(max_length=200, blank=True)
    name_ne = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_organic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def product_icon(self):
        name_lower = self.name.lower()
        
        # Check by keywords in English name
        if 'garlic' in name_lower: return '🧄'
        if 'onion' in name_lower: return '🧅'
        if 'tomato' in name_lower: return '🍅'
        if 'potato' in name_lower: return '🥔'
        if 'wheat' in name_lower: return '🌾'
        if 'rice' in name_lower: return '🍚'
        if 'turmeric' in name_lower: return '🫚'
        if 'mustard' in name_lower: return '🟡'
        if 'groundnut' in name_lower or 'peanut' in name_lower or 'badam' in name_lower: return '🥜'
        if 'chilli' in name_lower or 'chili' in name_lower or 'pepper' in name_lower: return '🌶'
        if 'mango' in name_lower: return '🥭'
        if 'banana' in name_lower: return '🍌'
        if 'apple' in name_lower: return '🍎'
        if 'orange' in name_lower: return '🍊'
        if 'grapes' in name_lower: return '🍇'
        if 'pomegranate' in name_lower: return '🍎'
        if 'papaya' in name_lower: return '🥭'
        if 'guava' in name_lower: return '🍏'
        if 'pineapple' in name_lower: return '🍍'
        if 'watermelon' in name_lower: return '🍉'
        if 'lemon' in name_lower: return '🍋'
        if 'coconut' in name_lower: return '🥥'
        if 'peach' in name_lower: return '🍑'
        if 'plum' in name_lower: return '🫐'
        if 'pear' in name_lower: return '🍐'
        if 'milk' in name_lower: return '🥛'
        if 'paneer' in name_lower: return '🧀'
        if 'ghee' in name_lower or 'butter' in name_lower: return '🧈'
        if 'curd' in name_lower or 'yogurt' in name_lower: return '🥣'
        if 'sesame' in name_lower: return '🫘'
        if 'sunflower' in name_lower: return '🌻'
        if 'soybean' in name_lower: return '🫛'
        if 'carrot' in name_lower: return '🥕'
        if 'cabbage' in name_lower or 'spinach' in name_lower or 'leaves' in name_lower: return '🥬'
        if 'cauliflower' in name_lower or 'broccoli' in name_lower: return '🥦'
        if 'eggplant' in name_lower or 'brinjal' in name_lower: return '🍆'
        if 'cucumber' in name_lower: return '🥒'
        if 'maize' in name_lower or 'corn' in name_lower: return '🌽'
        if 'barley' in name_lower or 'millet' in name_lower or 'oats' in name_lower or 'grain' in name_lower: return '🌾'
        if 'pea' in name_lower: return '🫛'
        if 'dal' in name_lower or 'pulse' in name_lower or 'lentil' in name_lower or 'gram' in name_lower or 'bean' in name_lower: return '🫘'
        if 'spices' in name_lower: return '🌶'
        
        # Fallback to category icon
        if self.category and self.category.icon:
            return self.category.icon
        return '🌾'

    @property
    def product_image_url(self):
        if self.image:
            return self.image.url
            
        from django.templatetags.static import static
        name_lower = self.name.lower()
        
        # Crop image mapping configurations
        crop_mappings = {
            'tomato': 'tomato.png',
            'cucumber': 'cucumber.png',
            'capsicum': 'capsicum.png',
            'bell pepper': 'capsicum.png',
            'cauliflower': 'cauliflower.png',
            'bottle gourd': 'bottle_gourd.png',
            'lauki': 'bottle_gourd.png',
            'garlic': 'garlic.png',
            'mustard': 'mustard.png',
            'groundnut': 'groundnut.png',
            'peanut': 'groundnut.png',
            'wheat': 'wheat.png',
            'potato': 'potato.png',
            'onion': 'onion.png',
            'spinach': 'spinach.png',
            'coconut': 'coconut.png',
            'cabbage': 'cabbage.png',
            'carrot': 'carrot.png',
            'radish': 'radish.png',
            'eggplant': 'eggplant.png',
            'brinjal': 'eggplant.png',
            'okra': 'okra.png',
            'bhindi': 'okra.png',
            'chilli powder': 'chilli_powder.png',
            'chili powder': 'chilli_powder.png',
            'chilli': 'chilli.png',
            'chili': 'chilli.png',
            'chickpea': 'chickpea.png',
            'pea': 'pea.png',
            'mango': 'mango.png',
            'banana': 'banana.png',
            'apple': 'apple.png',
            'orange': 'orange.png',
            'grapes': 'grapes.png',
            'pomegranate': 'pomegranate.png',
            'papaya': 'papaya.png',
            'guava': 'guava.png',
            'pineapple': 'pineapple.png',
            'watermelon': 'watermelon.png',
            'lemon': 'lemon.png',
            'strawberry': 'strawberry.png',
            'turmeric': 'turmeric.png',
            'cumin': 'cumin.png',
            'cardamom': 'cardamom.png',
            'cloves': 'cloves.png',
            'soybean': 'soybean.png',
            'sunflower': 'sunflower.png',
            'barley': 'barley.png',
            'millet': 'millet.png',
            'maize': 'maize.png',
            'corn': 'maize.png',
            'oats': 'oats.png',
            'ginger': 'ginger.png',
            'rice': 'rice.png',
            'paddy': 'rice.png',
        }
        
        for key, filename in crop_mappings.items():
            if key in name_lower:
                return static(f'images/products/{filename}')
                
        return None

    def save(self, *args, **kwargs):
        from .translation import translate_text
        if self.name:
            self.name_hi = translate_text(self.name, 'hi')
            self.name_ne = translate_text(self.name, 'ne')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} by {self.farmer.username}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
