from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MarketPrice
from .forms import MarketPriceForm

def price_list(request):
    prices = MarketPrice.objects.all()
    crop = request.GET.get('crop', '')
    state = request.GET.get('state', '')
    if crop:
        prices = prices.filter(crop_name__icontains=crop)
    if state:
        prices = prices.filter(state__icontains=state)
    states = MarketPrice.objects.values_list('state', flat=True).distinct()
    return render(request, 'prices/price_list.html', {'prices': prices, 'states': states, 'crop': crop, 'state': state})

@login_required
def add_price(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Admin access required.')
        return redirect('price_list')
    if request.method == 'POST':
        form = MarketPriceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Market price added! / मंडी भाव जोड़ा!')
            return redirect('price_list')
    else:
        form = MarketPriceForm()
    return render(request, 'prices/price_form.html', {'form': form})
