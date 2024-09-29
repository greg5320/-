
from django.contrib import admin
from django.urls import path
from bmstu_lab import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_maps, name='maps'),
    path('map/<int:map_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/<int:cart_id>/', views.view_cart, name='cart'),
    path('map/<int:id>/', views.get_map_detail, name='map_detail'),
    path('cart/<int:cart_id>/delete/', views.delete_cart, name='delete_cart'),
]

