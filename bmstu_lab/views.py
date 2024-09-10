from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import date

all_maps = [
    {'id': 1, 'title': 'Left 2 Die', 'image_url': 'http://127.0.0.1:9000/mybucket/Left_2_Die.webp', 'description': 'Описание карты Left 2 Die...'},
    {'id': 2, 'title': 'New Antioch', 'image_url': 'http://127.0.0.1:9000/mybucket/New_Antioch.webp', 'description': 'Описание карты New Antioch...'},
    {'id': 3, 'title': 'Aiur Chef', 'image_url': 'http://127.0.0.1:9000/mybucket/Aiur_Chef.webp', 'description': 'Описание карты Aiur Chef...'},
    {'id': 4, 'title': 'Lost Temple', 'image_url': 'http://127.0.0.1:9000/mybucket/Lost_temple.webp', 'description': 'Описание карты Lost Temple...'},
    {'id': 5, 'title': 'StarCraft Master', 'image_url': 'http://127.0.0.1:9000/mybucket/Starcraft_Master.webp', 'description': 'Описание карты StarCraft Master...'},
    {'id': 6, 'title': 'Atlas Station', 'image_url': 'http://127.0.0.1:9000/mybucket/Atlas_Station.webp', 'description': 'Описание карты Atlas Station...'},
    {'id': 7, 'title': 'Bastion of the Conclave', 'image_url': 'http://127.0.0.1:9000/mybucket/Bastion_of_the_Conclave.webp', 'description': 'Описание карты Bastion of the Conclave...'},
    {'id': 8, 'title': 'Moebius Facility XX-1', 'image_url': 'http://127.0.0.1:9000/mybucket/Moebius_Facility_XX1.webp', 'description': 'Описание карты Moebius Facility XX-1...'},
]


def get_maps(request):
    return render(request, 'maps.html', {'maps': all_maps})

def get_map_detail(request, id):
    map_detail = next((map for map in all_maps if map['id'] == id), None)
    if not map_detail:
        map_detail = {'title': 'Unknown Map', 'description': 'No description available.'}
    return render(request, 'map_detail.html', {'map': map_detail})

def add_to_cart(request, map_id):
    cart = request.session.get('cart', [])
    if map_id not in cart:
        cart.append(map_id)
    request.session['cart'] = cart
    return redirect('maps')


def view_cart(request):
    cart = request.session.get('cart', [])
    cart_maps = [map for map in all_maps if map['id'] in cart]
    return render(request, 'cart.html', {'cart_maps': cart_maps})