from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from marketplace.models import Product
from orders.models import Order

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name or user.username}! Account created successfully. / खाता सफलतापूर्वक बनाया गया!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! / वापस स्वागत है!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user, 'active_tab': 'dashboard'}
    if user.is_farmer:
        from django.db.models import Sum, Q
        context['my_products'] = Product.objects.filter(farmer=user).order_by('-created_at')[:5]
        context['my_orders'] = Order.objects.filter(product__farmer=user).select_related('product').order_by('-created_at')[:5]
        context['total_products'] = Product.objects.filter(farmer=user).count()
        context['total_orders'] = Order.objects.filter(product__farmer=user).count()
        
        sales_val = Order.objects.filter(product__farmer=user).exclude(status='cancelled').aggregate(total=Sum('total_price'))['total']
        context['total_sales'] = float(sales_val or 0)
        
        earnings_val = Order.objects.filter(product__farmer=user).filter(Q(status='delivered') | Q(payment_status='paid')).exclude(status='cancelled').aggregate(total=Sum('total_price'))['total']
        context['total_earnings'] = float(earnings_val or 0)
        
        context['pending_orders'] = Order.objects.filter(product__farmer=user, status='pending').count()
        context['completed_orders'] = Order.objects.filter(product__farmer=user, status='delivered').count()
    elif user.is_buyer:
        context['my_orders'] = Order.objects.filter(buyer=user).select_related('product').order_by('-created_at')[:5]
        context['total_orders'] = Order.objects.filter(buyer=user).count()
        context['delivered'] = Order.objects.filter(buyer=user, status='delivered').count()
        context['pending'] = Order.objects.filter(buyer=user, status='pending').count()
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated! / प्रोफाइल अपडेट हुई!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    context = {
        'form': form,
        'base_template': 'base_farmer.html' if request.user.is_farmer else 'base.html',
        'active_tab': 'profile'
    }
    return render(request, 'accounts/profile.html', context)

def social_login_view(request, provider):
    provider = provider.lower()
    if provider not in ['google', 'facebook', 'apple']:
        return redirect('login')
    
    provider_display = {
        'google': 'Google',
        'facebook': 'Facebook',
        'apple': 'Apple ID'
    }.get(provider, provider.title())
    
    selected_lang = request.session.get('selected_lang', 'en')
    
    return render(request, 'accounts/social_oauth.html', {
        'provider': provider,
        'provider_display': provider_display,
        'selected_lang': selected_lang
    })

def social_callback_view(request, provider):
    provider_display = {
        'google': 'Google',
        'facebook': 'Facebook',
        'apple': 'Apple ID'
    }.get(provider.lower(), provider.title())
    selected_lang = request.session.get('selected_lang', 'en')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'buyer').strip()
        phone = request.POST.get('phone', '').strip()
        state = request.POST.get('state', '').strip()
        district = request.POST.get('district', '').strip()
        
        if not email:
            messages.error(request, 'Email is required.')
            return redirect('social_login', provider=provider)
            
        base_username = email.split('@')[0]
        import re
        username = re.sub(r'[^a-zA-Z]', '', base_username)
        if not username:
            username = "socialuser"
            
        from accounts.models import CustomUser
        counter = 1
        orig_username = username
        while CustomUser.objects.filter(username=username).exists():
            username = f"{orig_username}{counter}"
            counter += 1
            
        user, created = CustomUser.objects.get_or_create(email=email, defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'phone': phone,
            'state': state,
            'district': district,
            'is_verified': True
        })
        
        if not created:
            updated = False
            if not user.first_name and first_name:
                user.first_name = first_name
                updated = True
            if not user.last_name and last_name:
                user.last_name = last_name
                updated = True
            if not user.phone and phone:
                user.phone = phone
                updated = True
            if not user.state and state:
                user.state = state
                updated = True
            if not user.district and district:
                user.district = district
                updated = True
            if updated:
                user.save()
                
        login(request, user)
        
        messages.success(
            request, 
            f'Welcome {user.first_name or user.username}! Login completed via {provider_display}.' if selected_lang == 'en' else
            f'स्वागत है, {user.first_name or user.username}! {provider_display} के माध्यम से लॉगिन पूर्ण हुआ।' if selected_lang == 'hi' else
            f'स्वागत छ, {user.first_name or user.username}! {provider_display} मार्फत लगइन पूरा भयो।'
        )
        return redirect('dashboard')
        
    return redirect('login')
