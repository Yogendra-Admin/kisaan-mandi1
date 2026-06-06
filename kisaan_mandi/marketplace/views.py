from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm

def product_list(request):
    products = Product.objects.filter(status='active').select_related('farmer', 'category')
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    state = request.GET.get('state', '')
    organic = request.GET.get('organic', '')
    sort = request.GET.get('sort', '-created_at')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(name_hi__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if state:
        products = products.filter(state__icontains=state)
    if organic:
        products = products.filter(is_organic=True)
    if sort in ['price_per_unit', '-price_per_unit', '-created_at', 'name']:
        products = products.order_by(sort)

    return render(request, 'marketplace/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().select_related('buyer')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            rev = review_form.save(commit=False)
            rev.product = product
            rev.buyer = request.user
            rev.save()
            messages.success(request, 'Review submitted! / समीक्षा सबमिट की!')
            return redirect('product_detail', pk=pk)
    return render(request, 'marketplace/product_detail.html', {
        'product': product, 'reviews': reviews, 'avg_rating': avg_rating, 'review_form': review_form
    })

@login_required
def add_product(request):
    if not request.user.is_farmer:
        messages.error(request, 'Only farmers can add products.')
        return redirect('product_list')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            messages.success(request, 'Product listed successfully! / उत्पाद सूचीबद्ध!')
            return redirect('my_products')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product / उत्पाद जोड़ें',
        'base_template': 'base_farmer.html' if request.user.is_farmer else 'base.html',
        'active_tab': 'add_product'
    }
    return render(request, 'marketplace/product_form.html', context)

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated! / उत्पाद अपडेट हुआ!')
            return redirect('my_products')
    else:
        form = ProductForm(instance=product)
        
    context = {
        'form': form,
        'title': 'Edit Product / संपादित करें',
        'base_template': 'base_farmer.html' if request.user.is_farmer else 'base.html',
        'active_tab': 'products'
    }
    return render(request, 'marketplace/product_form.html', context)

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted. / उत्पाद हटाया गया।')
    return redirect('my_products')

@login_required
def my_products(request):
    products = Product.objects.filter(farmer=request.user).order_by('-created_at')
    context = {
        'products': products,
        'base_template': 'base_farmer.html' if request.user.is_farmer else 'base.html',
        'active_tab': 'products'
    }
    return render(request, 'marketplace/my_products.html', context)
