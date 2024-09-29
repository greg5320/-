
from django.contrib import admin
from django.urls import path
from bmstu_lab import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.get_maps, name='maps'),
    path('map/<int:map_id>/add/', views.add_to_map_pool, name='add_to_map_pool'),
    path('map_pool/<int:map_pool_id>/', views.view_map_pool, name='map_pool'),
    path('map/<int:id>/', views.get_map_detail, name='map_detail'),
    path('map_pool/<int:map_pool_id>/delete/', views.delete_map_pool, name='delete_map_pool'),
]

