from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from .models import MapPool, MapMapPool, Map
from django.db import connection
def get_maps(request):
    map_pool, created = MapPool.objects.get_or_create(user=request.user, status='draft',defaults={'player_login': 'greg'})
    query = request.GET.get('map', '')
    if query:
        maps = Map.objects.filter(title__icontains=query)
    else:
        maps = Map.objects.all()
    map_pool_count = MapMapPool.objects.filter(map_pool=map_pool).count()
    return render(request, 'maps.html', {
        'maps': maps,
        'map_pool_count': map_pool_count,
        'map_pool_id': map_pool.id,
        'query': query
    })

def add_to_map_pool(request, map_id):
    map_obj = get_object_or_404(Map, id=map_id, status='active')
    user = request.user
    map_pool, created = MapPool.objects.get_or_create(user=user, status='draft')
    map_map_pool, created = MapMapPool.objects.get_or_create(map_pool=map_pool, map=map_obj, defaults={
        'position': MapMapPool.objects.filter(map_pool=map_pool).count() + 1
    })
    if not created:
        map_map_pool.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))



def view_map_pool(request, map_pool_id):
    map_pool = get_object_or_404(MapPool, id=map_pool_id)
    maps_in_map_pool = MapMapPool.objects.filter(map_pool=map_pool).order_by('position')
    return render(request, 'map_pool.html', {'map_pool': map_pool, 'maps_in_map_pool': maps_in_map_pool})

def get_map_detail(request, id):
    map_detail = get_object_or_404(Map, id=id)
    return render(request, 'map_detail.html', {'map': map_detail, 'request': request})


def delete_map_pool(request, map_pool_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE bmstu_lab_mappool
            SET status = %s
            WHERE id = %s
        """, ['deleted', map_pool_id])
    return redirect('maps')