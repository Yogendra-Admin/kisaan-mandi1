from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Cart, Notification
from .forms import OrderForm, CartOrderForm
from marketplace.models import Product

@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status='active')
    if request.user == product.farmer:
        messages.error(request, 'You cannot order your own product.')
        return redirect('product_detail', pk=product_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.buyer = request.user
            order.product = product
            order.total_price = order.quantity * product.price_per_unit
            order.save()
            
            # Send notifications
            Notification.send(
                user=order.product.farmer,
                message_en=f"New order #{order.id} received for {order.product.name}.",
                message_hi=f"à¤‰à¤¤à¥à¤ªà¤¾à¤¦ {order.product.name_hi or order.product.name} à¤•à¥‡ à¤²à¤¿à¤ à¤¨à¤¯à¤¾ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤†à¥¤",
                message_ne=f"à¤‰à¤¤à¥à¤ªà¤¾à¤¦à¤¨ {order.product.name_ne or order.product.name} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤¨à¤¯à¤¾à¤ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤­à¤¯à¥‹à¥¤"
            )
            Notification.send(
                user=request.user,
                message_en=f"Your order #{order.id} for {order.product.name} has been placed.",
                message_hi=f"{order.product.name_hi or order.product.name} à¤•à¥‡ à¤²à¤¿à¤ à¤†à¤ªà¤•à¤¾ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤¦à¤¿à¤¯à¤¾ à¤—à¤¯à¤¾ à¤¹à¥ˆà¥¤",
                message_ne=f"{order.product.name_ne or order.product.name} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤°à¤¾à¤–à¤¿à¤à¤•à¥‹ à¤›à¥¤"
            )
            
            # If online or upi payment is selected, redirect to payment checkout page
            if order.payment_method in ['online', 'upi']:
                return redirect('payment_checkout', order_id=order.id)
                
            messages.success(request, f'Order placed successfully! Order #{order.id} / à¤‘à¤°à¥à¤¡à¤° à¤¦à¤¿à¤¯à¤¾ à¤—à¤¯à¤¾!')
            return redirect('order_detail', pk=order.id)
    else:
        initial_qty = request.GET.get('quantity', '1.0')
        form = OrderForm(initial={
            'delivery_address': request.user.address,
            'quantity': initial_qty
        })
    return render(request, 'orders/place_order.html', {'form': form, 'product': product})

@login_required
def my_orders(request):
    status_filter = request.GET.get('status')
    if request.user.is_farmer:
        orders = Order.objects.filter(product__farmer=request.user).select_related('buyer', 'product')
    else:
        orders = Order.objects.filter(buyer=request.user).select_related('product')
        
    if status_filter:
        if status_filter in ['pending', 'confirmed', 'dispatched', 'delivered', 'cancelled']:
            orders = orders.filter(status=status_filter)
            
    orders = orders.order_by('-created_at')
    return render(request, 'orders/my_orders.html', {
        'orders': orders,
        'current_filter': status_filter,
        'base_template': 'base_farmer.html' if request.user.is_farmer else 'base.html',
        'active_tab': 'orders'
    })

@login_required
def order_detail(request, pk):
    if request.user.is_farmer:
        order = get_object_or_404(Order, pk=pk, product__farmer=request.user)
    else:
        order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'base_template': 'base_farmer.html' if request.user.is_farmer else 'base.html',
    })

def send_order_notifications(order, previous_status, new_status):
    from django.core.mail import send_mail
    import logging
    logger = logging.getLogger('orders.notifications')
    
    status_display = order.get_status_display()
    
    # 1. Email to Buyer
    buyer_email = order.buyer.email
    if buyer_email:
        subject = f"Kisaan Mandi - Order #{order.id} Status Update"
        message = (
            f"Dear {order.buyer.first_name or order.buyer.username},\n\n"
            f"Your order #{order.id} for '{order.product.name}' has been updated to '{status_display}'.\n\n"
            f"Thank you,\nKisaan Mandi Team"
        )
        try:
            send_mail(subject, message, 'no-reply@kisaanmandi.in', [buyer_email], fail_silently=True)
        except Exception as e:
            logger.error(f"Failed to send email to buyer: {e}")
            
    # 2. Email to Farmer
    farmer_email = order.product.farmer.email
    if farmer_email:
        subject = f"Kisaan Mandi - Order #{order.id} Status Update"
        message = (
            f"Dear {order.product.farmer.first_name or order.product.farmer.username},\n\n"
            f"The status of Order #{order.id} for your product '{order.product.name}' has been updated to '{status_display}'.\n\n"
            f"Thank you,\nKisaan Mandi Team"
        )
        try:
            send_mail(subject, message, 'no-reply@kisaanmandi.in', [farmer_email], fail_silently=True)
        except Exception as e:
            logger.error(f"Failed to send email to farmer: {e}")
            
    # 3. SMS to Buyer (Simulated via console logging)
    buyer_phone = order.buyer.phone
    if buyer_phone:
        sms_body = f"[SMS to {buyer_phone}]: Kisaan Mandi Order #{order.id} status updated to {status_display}."
        print(sms_body)
        logger.info(sms_body)
        
    # 4. SMS to Farmer (Simulated via console logging)
    farmer_phone = order.product.farmer.phone
    if farmer_phone:
        sms_body = f"[SMS to {farmer_phone}]: Kisaan Mandi Order #{order.id} status updated to {status_display}."
        print(sms_body)
        logger.info(sms_body)

@login_required
def update_order_status(request, pk):
    from django.db.models import Q
    order = get_object_or_404(Order, Q(buyer=request.user) | Q(product__farmer=request.user), pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            is_farmer = (order.product.farmer == request.user)
            is_buyer = (order.buyer == request.user)
            
            allowed = False
            error_msg = ""
            
            # Final state check
            if order.status in ['delivered', 'cancelled']:
                error_msg = "Cannot change status of a completed or cancelled order."
            else:
                if is_buyer:
                    if new_status == 'cancelled':
                        if order.status in ['pending', 'confirmed']:
                            allowed = True
                        else:
                            error_msg = "You can only cancel pending or confirmed orders. / à¤†à¤ª à¤•à¥‡à¤µà¤² à¤²à¤‚à¤¬à¤¿à¤¤ à¤¯à¤¾ à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤•à¥€ à¤—à¤ˆ à¤‘à¤°à¥à¤¡à¤° à¤°à¤¦à¥à¤¦ à¤•à¤° à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤"
                    elif new_status == 'delivered':
                        if order.status == 'dispatched':
                            allowed = True
                        else:
                            error_msg = "You can only mark dispatched orders as delivered. / à¤†à¤ª à¤•à¥‡à¤µà¤² à¤­à¥‡à¤œà¥‡ à¤—à¤ à¤‘à¤°à¥à¤¡à¤° à¤•à¥‹ à¤µà¤¿à¤¤à¤°à¤¿à¤¤ à¤šà¤¿à¤¹à¥à¤¨à¤¿à¤¤ à¤•à¤° à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤"
                    else:
                        error_msg = "Buyers are only allowed to cancel or confirm delivery. / à¤–à¤°à¥€à¤¦à¤¾à¤° à¤•à¥‡à¤µà¤² à¤‘à¤°à¥à¤¡à¤° à¤°à¤¦à¥à¤¦ à¤¯à¤¾ à¤µà¤¿à¤¤à¤°à¤£ à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤•à¤° à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤"
                elif is_farmer:
                    if new_status == 'delivered':
                        error_msg = "Only the buyer can confirm delivery of this order. / केवल खरीदार ही इस ऑर्डर के वितरण की पुष्टि कर सकते हैं।"
                    else:
                        allowed = True
            
            if allowed:
                previous_status = order.status
                order.status = new_status
                
                # If delivered and payment was COD, automatically mark as paid
                if new_status == 'delivered' and order.payment_method == 'cod':
                    order.payment_status = 'paid'
                    
                order.save()
                
                # Send email and SMS notifications
                send_order_notifications(order, previous_status, new_status)
                
                # Send notifications
                status_map = {
                    'pending': ('Pending', 'à¤ªà¥à¤°à¤¤à¥€à¤•à¥à¤·à¤¾à¤°à¤¤', 'à¤ªà¥à¤°à¤¤à¥€à¤•à¥à¤·à¤¾à¤°à¤¤'),
                    'confirmed': ('Confirmed', 'à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤•à¥€ à¤—à¤ˆ', 'à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤—à¤°à¤¿à¤¯à¥‹'),
                    'dispatched': ('Dispatched', 'à¤­à¥‡à¤œà¤¾ à¤—à¤¯à¤¾', 'à¤ªà¤ à¤¾à¤‡à¤¯à¥‹'),
                    'delivered': ('Delivered / Completed', 'à¤µà¤¿à¤¤à¤°à¤¿à¤¤', 'à¤µà¤¿à¤¤à¤°à¤£ à¤­à¤¯à¥‹'),
                    'cancelled': ('Cancelled', 'à¤°à¤¦à¥à¤¦ à¤•à¤¿à¤¯à¤¾ à¤—à¤¯à¤¾', 'à¤°à¤¦à¥à¤¦ à¤—à¤°à¤¿à¤¯à¥‹'),
                }
                s_en, s_hi, s_ne = status_map.get(new_status, (new_status, new_status, new_status))
                
                if is_buyer:
                    Notification.send(
                        user=order.buyer,
                        message_en=f"You updated order #{order.id} status to {s_en}.",
                        message_hi=f"à¤†à¤ªà¤¨à¥‡ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤•à¥€ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_hi}' à¤ªà¤° à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤•à¤° à¤¦à¥€ à¤¹à¥ˆà¥¤",
                        message_ne=f"à¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤•à¥‹ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_ne}' à¤®à¤¾ à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤­à¤à¤•à¥‹ à¤›à¥¤"
                    )
                    Notification.send(
                        user=order.product.farmer,
                        message_en=f"Buyer updated order #{order.id} status to {s_en}.",
                        message_hi=f"à¤–à¤°à¥€à¤¦à¤¾à¤° à¤¨à¥‡ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤•à¥€ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_hi}' à¤ªà¤° à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤•à¤° à¤¦à¥€ à¤¹à¥ˆà¥¤",
                        message_ne=f"à¤–à¤°à¤¿à¤¦à¤•à¤°à¥à¤¤à¤¾à¤²à¥‡ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤•à¥‹ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_ne}' à¤®à¤¾ à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤­à¤à¤•à¥‹ à¤›à¥¤"
                    )
                else:
                    Notification.send(
                        user=order.buyer,
                        message_en=f"Your order #{order.id} status updated to {s_en}.",
                        message_hi=f"à¤†à¤ªà¤•à¥‡ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤•à¥€ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_hi}' à¤®à¥‡à¤‚ à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤¹à¥‹ à¤—à¤ˆ à¤¹à¥ˆà¥¤",
                        message_ne=f"à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤•à¥‹ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_ne}' à¤®à¤¾ à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤­à¤à¤•à¥‹ à¤›à¥¤"
                    )
                    Notification.send(
                        user=order.product.farmer,
                        message_en=f"You updated order #{order.id} status to {s_en}.",
                        message_hi=f"à¤†à¤ªà¤¨à¥‡ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤•à¥€ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_hi}' à¤ªà¤° à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤•à¤° à¤¦à¥€ à¤¹à¥ˆà¥¤",
                        message_ne=f"à¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤•à¥‹ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ '{s_ne}' à¤®à¤¾ à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤­à¤à¤•à¥‹ à¤›à¥¤"
                    )
                
                messages.success(request, f'Order status updated to {order.get_status_display()}!')
            else:
                messages.error(request, error_msg or 'Invalid status transition / à¤…à¤®à¤¾à¤¨à¥à¤¯ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ à¤¸à¤‚à¤•à¥à¤°à¤®à¤£à¥¤')
                
    return redirect('order_detail', pk=pk)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status='active')
    
    from decimal import Decimal, InvalidOperation
    qty = Decimal('1.0')
    if request.method == 'POST':
        qty_str = request.POST.get('quantity')
    else:
        qty_str = request.GET.get('quantity')
        
    if qty_str:
        try:
            qty = Decimal(qty_str)
            if qty <= Decimal('0'):
                qty = Decimal('1.0')
        except (ValueError, TypeError, InvalidOperation):
            qty = Decimal('1.0')
            
    cart_item, created = Cart.objects.get_or_create(
        buyer=request.user, 
        product=product,
        defaults={'quantity': qty}
    )
    if not created:
        # Convert qty to Decimal to avoid type mismatch
        cart_item.quantity += Decimal(str(qty))
        
    if cart_item.quantity > product.quantity_available:
        cart_item.quantity = product.quantity_available
        
    cart_item.save()
    messages.success(request, 'Added to cart! / à¤•à¤¾à¤°à¥à¤Ÿ à¤®à¥‡à¤‚ à¤œà¥‹à¤¡à¤¼à¤¾!')
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(buyer=request.user).select_related('product')
    total = sum(item.product.price_per_unit * item.quantity for item in cart_items)
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def place_cart_order(request):
    cart_items = Cart.objects.filter(buyer=request.user).select_related('product')
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty. / à¤†à¤ªà¤•à¤¾ à¤•à¤¾à¤°à¥à¤Ÿ à¤–à¤¾à¤²à¥€ à¤¹à¥ˆà¥¤ / à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤•à¤¾à¤°à¥à¤Ÿ à¤–à¤¾à¤²à¥€ à¤›à¥¤')
        return redirect('cart')
        
    total_price = sum(item.product.price_per_unit * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        form = CartOrderForm(request.POST)
        if form.is_valid():
            import uuid
            group_id = f"cart_{uuid.uuid4().hex[:12]}"
            created_orders = []
            
            for item in cart_items:
                order = Order(
                    buyer=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.product.price_per_unit * item.quantity,
                    payment_method=form.cleaned_data['payment_method'],
                    delivery_address=form.cleaned_data['delivery_address'],
                    notes=form.cleaned_data.get('notes', ''),
                    status='pending',
                    payment_status='pending',
                    razorpay_order_id=group_id
                )
                order.save()
                
                # Send notifications per order item to the farmer
                Notification.send(
                    user=order.product.farmer,
                    message_en=f"New order #{order.id} received for {order.product.name} via cart.",
                    message_hi=f"à¤•à¤¾à¤°à¥à¤Ÿ à¤•à¥‡ à¤®à¤¾à¤§à¥à¤¯à¤® à¤¸à¥‡ à¤‰à¤¤à¥à¤ªà¤¾à¤¦ {order.product.name_hi or order.product.name} à¤•à¥‡ à¤²à¤¿à¤ à¤¨à¤¯à¤¾ à¤‘à¤°à¥à¤¡à¤° #{order.id} à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤†à¥¤",
                    message_ne=f"à¤•à¤¾à¤°à¥à¤Ÿ à¤®à¤¾à¤°à¥à¤«à¤¤ à¤‰à¤¤à¥à¤ªà¤¾à¤¦à¤¨ {order.product.name_ne or order.product.name} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤¨à¤¯à¤¾à¤ à¤…à¤°à¥à¤¡à¤° #{order.id} à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤­à¤¯à¥‹à¥¤"
                )
                created_orders.append(order)
                
            # Send summary notification to the buyer
            Notification.send(
                user=request.user,
                message_en=f"Your cart checkout completed. {len(created_orders)} orders placed successfully.",
                message_hi=f"à¤†à¤ªà¤•à¤¾ à¤•à¤¾à¤°à¥à¤Ÿ à¤šà¥‡à¤•à¤†à¤‰à¤Ÿ à¤ªà¥‚à¤°à¤¾ à¤¹à¥à¤†à¥¤ {len(created_orders)} à¤‘à¤°à¥à¤¡à¤° à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¦à¤¿à¤ à¤—à¤ à¤¹à¥ˆà¤‚à¥¤",
                message_ne=f"à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤•à¤¾à¤°à¥à¤Ÿ à¤šà¥‡à¤•à¤†à¤‰à¤Ÿ à¤ªà¥‚à¤°à¤¾ à¤­à¤¯à¥‹à¥¤ {len(created_orders)} à¤…à¤°à¥à¤¡à¤°à¤¹à¤°à¥‚ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤°à¤¾à¤–à¤¿à¤à¤•à¤¾ à¤›à¤¨à¥à¥¤"
            )
            
            # Clear cart only if payment method is not online or upi (e.g. COD).
            # For online/upi, we only clear the cart after payment succeeds.
            if form.cleaned_data['payment_method'] not in ['online', 'upi']:
                cart_items.delete()
            
            # If online or upi payment is selected, redirect to payment checkout page
            if form.cleaned_data['payment_method'] in ['online', 'upi']:
                return redirect('payment_checkout', order_id=created_orders[0].id)
                
            messages.success(request, 'Orders placed successfully! / à¤‘à¤°à¥à¤¡à¤° à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¦à¤¿à¤ à¤—à¤! / à¤…à¤°à¥à¤¡à¤° à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤°à¤¾à¤–à¤¿à¤¯à¥‹!')
            return redirect('my_orders')
    else:
        form = CartOrderForm(initial={'delivery_address': request.user.address})
        
    return render(request, 'orders/place_cart_order.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def remove_from_cart(request, cart_id):
    Cart.objects.filter(pk=cart_id, buyer=request.user).delete()
    return redirect('cart')

@login_required
def update_cart_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, pk=cart_id, buyer=request.user)
    if request.method == 'POST':
        try:
            qty = float(request.POST.get('quantity'))
            if qty > 0:
                if qty <= cart_item.product.quantity_available:
                    cart_item.quantity = qty
                    cart_item.save()
                    messages.success(request, 'Quantity updated. / à¤®à¤¾à¤¤à¥à¤°à¤¾ à¤…à¤ªà¤¡à¥‡à¤Ÿ à¤•à¥€ à¤—à¤ˆà¥¤')
                else:
                    messages.error(
                        request, 
                        f"Only {cart_item.product.quantity_available} {cart_item.product.unit} available. / à¤•à¥‡à¤µà¤² {cart_item.product.quantity_available} à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¹à¥ˆà¥¤"
                    )
            else:
                messages.error(request, 'Quantity must be greater than zero. / à¤®à¤¾à¤¤à¥à¤°à¤¾ à¤¶à¥‚à¤¨à¥à¤¯ à¤¸à¥‡ à¤…à¤§à¤¿à¤• à¤¹à¥‹à¤¨à¥€ à¤šà¤¾à¤¹à¤¿à¤à¥¤')
        except (ValueError, TypeError):
            pass
    return redirect('cart')

@login_required
def payment_checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    if order.payment_status == 'paid':
        messages.info(request, 'This order is already paid. / à¤‡à¤¸ à¤‘à¤°à¥à¤¡à¤° à¤•à¤¾ à¤ªà¤¹à¤²à¥‡ à¤¹à¥€ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¹à¥‹ à¤šà¥à¤•à¤¾ à¤¹à¥ˆà¥¤')
        return redirect('order_detail', pk=order.id)
    if order.payment_method == 'cod':
        messages.error(request, 'Cash on Delivery orders cannot be paid online. / à¤¸à¥€à¤“à¤¡à¥€ à¤‘à¤°à¥à¤¡à¤°à¥à¤¸ à¤•à¤¾ à¤‘à¤¨à¤²à¤¾à¤‡à¤¨ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¨à¤¹à¥€à¤‚ à¤•à¤¿à¤¯à¤¾ à¤œà¤¾ à¤¸à¤•à¤¤à¤¾à¥¤')
        return redirect('order_detail', pk=order.id)
        
    razorpay_order_id = order.razorpay_order_id
    if razorpay_order_id:
        orders = Order.objects.filter(buyer=request.user, razorpay_order_id=razorpay_order_id)
    else:
        orders = Order.objects.filter(pk=order_id)
        
    total_price = sum(o.total_price for o in orders)
        
    from django.conf import settings
    import razorpay
    
    is_dummy = (
        not settings.RAZORPAY_KEY_ID or
        not settings.RAZORPAY_KEY_SECRET or
        settings.RAZORPAY_KEY_ID.startswith('rzp_test_dummy') or
        settings.RAZORPAY_KEY_SECRET == 'dummysecret12345'
    )
    is_mock = is_dummy
    
    if not is_dummy:
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount_paise = int(total_price * 100)
            notes = {
                'order_ids': ",".join(str(o.id) for o in orders),
                'buyer': order.buyer.username
            }
            if not razorpay_order_id or not razorpay_order_id.startswith('order_'):
                razorpay_order = client.order.create(dict(
                    amount=amount_paise,
                    currency='INR',
                    payment_capture='1',
                    notes=notes
                ))
                new_razorpay_order_id = razorpay_order['id']
                orders.update(razorpay_order_id=new_razorpay_order_id)
                razorpay_order_id = new_razorpay_order_id
        except Exception as e:
            is_mock = True
            
    if is_mock and (not razorpay_order_id or not razorpay_order_id.startswith('order_')):
        import time
        new_razorpay_order_id = f"order_mock_{order.id}_{int(time.time())}"
        orders.update(razorpay_order_id=new_razorpay_order_id)
        razorpay_order_id = new_razorpay_order_id
        
    context = {
        'order': order,
        'orders': orders,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order_id,
        'amount_paise': int(total_price * 100),
        'total_price': total_price,
        'is_mock': is_mock,
    }
    return render(request, 'orders/payment.html', context)

@login_required
@csrf_exempt
def payment_verify(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    if request.method == 'POST':
        utr_number = request.POST.get('utr_number')
        
        # Get grouped orders sharing same razorpay_order_id (uuid group id)
        group_orders = Order.objects.filter(buyer=request.user, razorpay_order_id=order.razorpay_order_id)
        if not group_orders.exists():
            group_orders = Order.objects.filter(pk=order_id)
            
        if utr_number:
            # Direct UPI Payment Verification
            for o in group_orders:
                o.payment_status = 'paid'
                o.status = 'confirmed'
                o.razorpay_payment_id = utr_number
                o.razorpay_signature = f"utr_verified_{utr_number}"
                o.save()
                
                # Send notifications
                Notification.send(
                    user=o.buyer,
                    message_en=f"UPI Payment verified for order #{o.id}. Order is now Confirmed.",
                    message_hi=f"à¤‘à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‡ à¤²à¤¿à¤ à¤¯à¥‚à¤ªà¥€à¤†à¤ˆ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤à¥¤ à¤‘à¤°à¥à¤¡à¤° à¤…à¤¬ 'à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤•à¥€ à¤—à¤ˆ' à¤¹à¥ˆà¥¤",
                    message_ne=f"à¤…à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤¯à¥‚à¤ªà¥€à¤†à¤ˆ à¤­à¥à¤•à¥à¤¤à¤¾à¤¨à¥€ à¤ªà¥à¤°à¤®à¤¾à¤£à¤¿à¤¤ à¤­à¤¯à¥‹à¥¤ à¤…à¤°à¥à¤¡à¤° à¤…à¤¬ 'à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤—à¤°à¤¿à¤¯à¥‹' à¤­à¤à¤•à¥‹ à¤›à¥¤"
                )
                Notification.send(
                    user=o.product.farmer,
                    message_en=f"Payment received for order #{o.id}. Please prepare for shipment.",
                    message_hi=f"à¤‘à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‡ à¤²à¤¿à¤ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤†à¥¤ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤¶à¤¿à¤ªà¤®à¥‡à¤‚à¤Ÿ à¤•à¥€ à¤¤à¥ˆà¤¯à¤¾à¤°à¥€ à¤•à¤°à¥‡à¤‚à¥¤",
                    message_ne=f"à¤…à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤­à¥à¤•à¥à¤¤à¤¾à¤¨à¥€ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤­à¤¯à¥‹à¥¤ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤¢à¥à¤µà¤¾à¤¨à¥€à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤¤à¤¯à¤¾à¤°à¥€ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥à¥¤"
                )
            messages.success(request, f'UPI Payment Verification submitted! UTR #{utr_number} / à¤¯à¥‚à¤ªà¥€à¤†à¤ˆ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤!')
            Cart.objects.filter(buyer=request.user).delete()
            return redirect('payment_success', order_id=order.id)
            
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        is_mocked = request.POST.get('is_mocked') == 'true'
        
        from django.conf import settings
        
        is_dummy = (not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET
                    or settings.RAZORPAY_KEY_ID.startswith('rzp_test_dummy')
                    or settings.RAZORPAY_KEY_SECRET == 'dummysecret12345')
        
        group_orders = Order.objects.filter(buyer=request.user, razorpay_order_id=razorpay_order_id)
        if not group_orders.exists():
            group_orders = Order.objects.filter(pk=order_id)
            
        if is_mocked or is_dummy:
            for o in group_orders:
                o.payment_status = 'paid'
                o.status = 'confirmed'
                o.razorpay_payment_id = razorpay_payment_id or f"pay_mock_{o.id}"
                o.razorpay_signature = razorpay_signature or "mock_signature_verified"
                o.save()
                
                # Send notifications
                Notification.send(
                    user=o.buyer,
                    message_en=f"Payment simulated successfully for order #{o.id}. Order Confirmed.",
                    message_hi=f"à¤‘à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‡ à¤²à¤¿à¤ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤…à¤¨à¥à¤•à¤°à¤£ à¤•à¤¿à¤¯à¤¾ à¤—à¤¯à¤¾à¥¤ à¤‘à¤°à¥à¤¡à¤° à¤•à¥€ à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤¹à¥à¤ˆà¥¤",
                    message_ne=f"à¤…à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤­à¥à¤•à¥à¤¤à¤¾à¤¨à¥€ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¸à¤¿à¤®à¥à¤²à¥‡à¤Ÿ à¤­à¤¯à¥‹à¥¤ à¤…à¤°à¥à¤¡à¤° à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤­à¤¯à¥‹à¥¤"
                )
                Notification.send(
                    user=o.product.farmer,
                    message_en=f"Payment received for order #{o.id}. Please dispatch the order.",
                    message_hi=f"à¤‘à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‡ à¤²à¤¿à¤ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤†à¥¤ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤‘à¤°à¥à¤¡à¤° à¤­à¥‡à¤œà¥‡à¤‚à¥¤",
                    message_ne=f"à¤…à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤­à¥à¤•à¥à¤¤à¤¾à¤¨à¥€ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤­à¤¯à¥‹à¥¤ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤…à¤°à¥à¤¡à¤° à¤ªà¤ à¤¾à¤‰à¤¨à¥à¤¹à¥‹à¤¸à¥à¥¤"
                )
            messages.success(request, 'Payment Simulated Successfully! / à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤«à¤² à¤°à¤¹à¤¾!')
            Cart.objects.filter(buyer=request.user).delete()
            return redirect('payment_success', order_id=order.id)
        else:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
                for o in group_orders:
                    o.payment_status = 'paid'
                    o.status = 'confirmed'
                    o.razorpay_payment_id = razorpay_payment_id
                    o.razorpay_signature = razorpay_signature
                    o.save()
                    
                    # Send notifications
                    Notification.send(
                        user=o.buyer,
                        message_en=f"Payment received successfully for order #{o.id}. Order Confirmed.",
                        message_hi=f"à¤‘à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‡ à¤²à¤¿à¤ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤†à¥¤ à¤‘à¤°à¥à¤¡à¤° à¤•à¥€ à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤¹à¥à¤ˆà¥¤",
                        message_ne=f"à¤…à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤­à¥à¤•à¥à¤¤à¤¾à¤¨à¥€ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤­à¤¯à¥‹à¥¤ à¤…à¤°à¥à¤¡à¤° à¤ªà¥à¤·à¥à¤Ÿà¤¿ à¤­à¤¯à¥‹à¥¤"
                    )
                    Notification.send(
                        user=o.product.farmer,
                        message_en=f"Payment received for order #{o.id}. Please dispatch the order.",
                        message_hi=f"à¤‘à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‡ à¤²à¤¿à¤ à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤†à¥¤ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤‘à¤°à¥à¤¡à¤° à¤­à¥‡à¤œà¥‡à¤‚à¥¤",
                        message_ne=f"à¤…à¤°à¥à¤¡à¤° #{o.id} à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤­à¥à¤•à¥à¤¤à¤¾à¤¨à¥€ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤­à¤¯à¥‹à¥¤ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤…à¤°à¥à¤¡à¤° à¤ªà¤ à¤¾à¤‰à¤¨à¥à¤¹à¥‹à¤¸à¥à¥¤"
                    )
                messages.success(request, 'Payment Received Successfully! / à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤«à¤² à¤°à¤¹à¤¾!')
                Cart.objects.filter(buyer=request.user).delete()
                return redirect('payment_success', order_id=order.id)
            except Exception as e:
                for o in group_orders:
                    o.payment_status = 'failed'
                    o.save()
                messages.error(request, f'Payment Verification Failed: {str(e)} / à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¨ à¤µà¤¿à¤«à¤² à¤°à¤¹à¤¾à¥¤')
                return redirect('payment_failed', order_id=order.id)
                
    return redirect('order_detail', pk=order.id)

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    return render(request, 'orders/payment_success.html', {'order': order})

@login_required
def payment_failed(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    return render(request, 'orders/payment_failed.html', {'order': order})

@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'home')

@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'home')

@login_required
def sales_report(request):
    if not request.user.is_farmer:
        return redirect('home')
        
    from django.db.models import Q
    delivered_orders = Order.objects.filter(
        product__farmer=request.user
    ).filter(
        Q(status='delivered') | Q(payment_status='paid')
    ).exclude(status='cancelled').select_related('buyer', 'product').order_by('-created_at')
    
    total_sales_count = delivered_orders.count()
    total_revenue = sum(o.total_price for o in delivered_orders)
    total_qty = sum(o.quantity for o in delivered_orders)
    avg_order_value = total_revenue / total_sales_count if total_sales_count > 0 else 0
    
    from django.utils import timezone
    from django.db.models.functions import ExtractMonth
    from django.db.models import Sum
    import datetime
    
    today = timezone.now()
    six_months_ago = today - datetime.timedelta(days=180)
    
    monthly_sales_query = Order.objects.filter(
        product__farmer=request.user,
        created_at__gte=six_months_ago
    ).filter(
        Q(status='delivered') | Q(payment_status='paid')
    ).exclude(status='cancelled').annotate(month=ExtractMonth('created_at')).values('month').annotate(total=Sum('total_price')).order_by('month')
    
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    sales_data = []
    for i in range(5, -1, -1):
        m_date = today - datetime.timedelta(days=i*30)
        m_num = m_date.month
        m_name = month_names[m_num]
        
        m_sum = 0
        for item in monthly_sales_query:
            if item['month'] == m_num:
                m_sum = float(item['total'] or 0)
                break
        sales_data.append({
            'month': m_name,
            'total': m_sum
        })
        
    max_total = max(x['total'] for x in sales_data) if sales_data else 0
    if max_total == 0:
        max_total = 1000.0
        
    points_list = []
    for idx, item in enumerate(sales_data):
        x = 50 + idx * 100
        y = 220 - (item['total'] / max_total * 180)
        item['x'] = x
        item['y'] = y
        points_list.append(f"{x},{y}")
        
    svg_points = " ".join(points_list)
        
    context = {
        'orders': delivered_orders,
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'total_qty': total_qty,
        'avg_order_value': avg_order_value,
        'sales_data': sales_data,
        'svg_points': svg_points,
        'max_total': max_total,
        'active_tab': 'sales'
    }
    return render(request, 'orders/sales_report.html', context)

@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/notifications_list.html', {
        'notifications': notifs,
        'active_tab': 'messages'
    })
