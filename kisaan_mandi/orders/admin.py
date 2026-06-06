from django.contrib import admin
from .models import Order, Cart

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'product', 'quantity', 'total_price', 'status', 'payment_method', 'payment_status', 'razorpay_order_id', 'razorpay_payment_id', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status']
    search_fields = ['buyer__username', 'product__name', 'razorpay_order_id', 'razorpay_payment_id']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'product', 'quantity', 'added_at']
