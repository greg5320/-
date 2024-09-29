from django.contrib import admin
from .models import Map, Cart, MapCart

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'players', 'tileset')
    search_fields = ('title',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'creation_date')
    list_filter = ('status',)

@admin.register(MapCart)
class MapCartAdmin(admin.ModelAdmin):
    list_display = ('cart', 'get_map_title', 'position')
    list_filter = ('cart',)

    def get_map_title(self, obj):
        return obj.map.title if obj.map else 'Нет карты'  # Предполагается, что у вас есть поле 'map' в модели

    get_map_title.short_description = 'Название карты'  # Заголовок для столбца