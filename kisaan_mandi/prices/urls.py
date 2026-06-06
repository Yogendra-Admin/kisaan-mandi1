from django.urls import path
from . import views
urlpatterns = [
    path('', views.price_list, name='price_list'),
    path('add/', views.add_price, name='add_price'),
]
