from django.urls import path
from .views import (
    MapList, MapDetail, AddMapToDraft,
    UploadImageForMap,
    MapPoolListView, MapPoolDetailView,
    MapPoolSubmitView, CompleteOrRejectMapPool, RegisterView, UserLogin, UserUpdate, UserLogout,
     RemoveMapFromMapPool, UpdateMapPosition, UpdateMapPosition
)

urlpatterns = [
    path('maps/', MapList.as_view(), name='map-list'),
    path('maps/<int:id>/', MapDetail.as_view(), name='map-detail'),
    path('maps/<int:id>/image/', UploadImageForMap.as_view(), name='upload-image'),
    path('maps/draft/', AddMapToDraft.as_view(), name='add-map-to-draft'),
    path('map_pools/', MapPoolListView.as_view(), name='map_pool_list'),
    path('map_pools/<int:id>/', MapPoolDetailView.as_view(), name='map_pool-detail'),
    path('map_pools/<int:id>/submit/', MapPoolSubmitView.as_view(), name='map_pool-submit'),
    path('map_pools/<int:id>/complete/', CompleteOrRejectMapPool.as_view(), name='map_pool-complete'),
    path('users/register/', RegisterView.as_view(), name='user-register'),
    path('users/login/', UserLogin.as_view(), name='user-login'),
    path('users/profile/', UserUpdate.as_view(), name='user-profile'),
    path('users/logout/', UserLogout.as_view(), name='user-logout'),
    path('map_pools/<int:map_pool_id>/map/<int:map_id>/',RemoveMapFromMapPool.as_view(), name='remove-map-from-map-pool'),
    path('map_pools/<int:map_pool_id>/map/<int:map_id>/position/', UpdateMapPosition.as_view(), name='update-map-position'),

]
