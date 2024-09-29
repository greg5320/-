from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from .models import Cart, MapCart, Map
from django.db import connection
def get_maps(request):
    cart, created = Cart.objects.get_or_create(user=request.user, status='draft')
    maps = Map.objects.all()
    cart_count = MapCart.objects.filter(cart=cart).count()

    return render(request, 'maps.html', {'maps': maps, 'cart_count': cart_count, 'cart_id': cart.id})

def add_to_cart(request, map_id):
    map_obj = get_object_or_404(Map, id=map_id, status='active')
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user, status='draft')
    map_cart, created = MapCart.objects.get_or_create(cart=cart, map=map_obj, defaults={
        'position': MapCart.objects.filter(cart=cart).count() + 1
    })
    if not created:
        map_cart.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))



def view_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
    maps_in_cart = MapCart.objects.filter(cart=cart).order_by('position')  # Сортируем по position
    return render(request, 'cart.html', {'cart': cart, 'maps_in_cart': maps_in_cart})

def get_map_detail(request, id):
    map_detail = get_object_or_404(Map, id=id)
    return render(request, 'map_detail.html', {'map': map_detail, 'request': request})


def delete_cart(request, cart_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE bmstu_lab_cart
            SET status = %s
            WHERE id = %s
        """, ['deleted', cart_id])
    return redirect('maps')