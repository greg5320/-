
from django.contrib import admin
from django.urls import path
from bmstu_lab import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_maps, name='maps'),
    path('map/<int:id>/', views.get_map_detail, name='map_detail'),
    path('add_to_cart/<int:map_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
]

