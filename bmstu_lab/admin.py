from django.contrib import admin
from .models import Map, MapPool, MapMapPool

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'players', 'tileset')
    search_fields = ('title',)

@admin.register(MapPool)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'creation_date')
    list_filter = ('status',)

@admin.register(MapMapPool)
class MapCartAdmin(admin.ModelAdmin):
    list_display = ('map_pool', 'get_map_title', 'position')
    list_filter = ('map_pool',)

    def get_map_title(self, obj):
        return obj.map.title if obj.map else 'Нет карты'

    get_map_title.short_description = 'Название карты'