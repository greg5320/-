from django.http import HttpResponse
from django.shortcuts import render, redirect
from .maps_data import all_maps
from .cart_data import cart_maps

def get_maps(request):
    query = request.GET.get('map', '')
    cart_count = len(cart_maps['maps'])
    filtered_maps = [map for map in all_maps if query.lower() in map['title'].lower()]
    return render(request, 'maps.html', {'maps': filtered_maps,'cart_count': cart_count})

def get_map_detail(request, id):
    map_detail = next((map for map in all_maps if map['id'] == id), None)
    if not map_detail:
        return HttpResponse('Карта не найдена', status=404)
    return render(request, 'map_detail.html', {'map': map_detail, 'request': request})


def view_cart(request, cart_id):
    cart = cart_maps if cart_maps['id'] == cart_id else None
    if not cart:
        return HttpResponse('Корзина не найдена', status=404)
    cart_items = cart['maps']
    return render(request, 'cart.html', {'cart_maps': cart_items, 'cart_id': cart_id})