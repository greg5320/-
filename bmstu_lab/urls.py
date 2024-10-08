from django.urls import path
from .views import (
    MapList, MapDetail, AddMapToDraft,
    UserProfileUpdate, UserLogin, user_logout, UploadImageForMap,
    MapPoolListView, AuthUserCreateView, MapPoolDetailView, MapPoolUpdateView,
    MapPoolFinalizeView, MapPoolDeleteView, MapMapPoolDeleteView, MapMapPoolUpdatePositionView
)

urlpatterns = [
    path('maps/', MapList.as_view(), name='map-list'),
    path('maps/<int:pk>/', MapDetail.as_view(), name='map-detail'),

    path('maps/<int:pk>/upload-image/', UploadImageForMap.as_view(), name='upload-image'),
    path('map_pools/draft/', AddMapToDraft.as_view(), name='add-map-to-draft'),
    path('map_pools/', MapPoolListView.as_view(), name='map_pool_list'),
    path('map_pools/<int:pk>/', MapPoolDetailView.as_view(), name='map_pool-detail'),
    path('map_pools/<int:pk>/update/', MapPoolUpdateView.as_view(), name='map_pool-update'),
    path('map_pools/<int:pk>/finalize/', MapPoolFinalizeView.as_view(), name='map_pool-finalize'),
    path('map_pools/<int:pk>/delete/', MapPoolDeleteView.as_view(), name='map_pool-delete'),
    path('map_pools/<int:pk>/remove/', MapMapPoolDeleteView.as_view(), name='map_map_pool_delete'),

    path('map_pools/<int:map_pool_id>/update_position/', MapMapPoolUpdatePositionView.as_view(),
         name='map_map_pool_update_position'),
    path('register/', AuthUserCreateView.as_view(), name='user-register'),
    path('profile/', UserProfileUpdate.as_view(), name='user-profile-update'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', user_logout, name='user-logout'),

]
