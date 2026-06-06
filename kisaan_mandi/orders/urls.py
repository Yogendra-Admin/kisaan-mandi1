from django.urls import path
from . import views
urlpatterns = [
    path('place/<int:product_id>/', views.place_order, name='place_order'),
    path('my/', views.my_orders, name='my_orders'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/status/', views.update_order_status, name='update_order_status'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.place_cart_order, name='place_cart_order'),
    path('cart/update/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('<int:order_id>/payment/', views.payment_checkout, name='payment_checkout'),
    path('<int:order_id>/payment/verify/', views.payment_verify, name='payment_verify'),
    path('<int:order_id>/payment/success/', views.payment_success, name='payment_success'),
    path('<int:order_id>/payment/failed/', views.payment_failed, name='payment_failed'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('notifications-list/', views.notifications_list, name='notifications_list'),
]
