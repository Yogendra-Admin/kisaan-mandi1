from django.shortcuts import render, redirect
from marketplace.models import Product, Category
from prices.models import MarketPrice

def home(request):
    # Old splash page removed — go straight to login or marketplace
    if request.user.is_authenticated:
        return redirect('product_list')
    return redirect('login')





def about(request):
    return render(request, 'core/about.html')

def set_language(request):
    """Save the chosen language in a cookie and redirect back."""
    lang = request.GET.get('lang', 'en')
    if lang not in ('en', 'hi', 'ne'):
        lang = 'en'
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER', '/')
    response = redirect(next_url)
    response.set_cookie('km_lang', lang, max_age=60 * 60 * 24 * 365)  # 1 year
    return response
