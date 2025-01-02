from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework import routers

from . import views
from .views import (
    MapList, MapDetail, AddMapToDraft,
    UploadImageForMap,
    MapPoolListView, MapPoolDetailView,
    MapPoolSubmitView, CompleteOrRejectMapPool, RemoveMapFromMapPool,
    UpdateMapPosition, RegisterView, UserLogin, ProfileView
)

router = routers.DefaultRouter()
# router.register(r'user', views.UserViewSet, basename='user')
schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/maps/', MapList.as_view(), name='map-list'),
    path('api/maps/<int:id>/', MapDetail.as_view(), name='map-detail'),
    path('api/maps/<int:id>/image/', UploadImageForMap.as_view(), name='upload-image'),
    path('api/maps/draft/', AddMapToDraft.as_view(), name='add-map-to-draft'),
    path('api/map_pools/', MapPoolListView.as_view(), name='map_pool_list'),
    path('api/map_pools/<int:id>/', MapPoolDetailView.as_view(), name='map_pool-detail'),
    path('api/map_pools/<int:id>/submit/', MapPoolSubmitView.as_view(), name='map_pool-submit'),
    path('api/map_pools/<int:id>/complete/', CompleteOrRejectMapPool.as_view(), name='map_pool-complete'),
    path('api/users/register/', RegisterView.as_view(), name='user-register'),
    path('api/users/profile/', ProfileView.as_view(), name='user-profile'),
    path('api/map_pools/<int:map_pool_id>/map/<int:map_id>/', RemoveMapFromMapPool.as_view(),
         name='remove-map-from-map-pool'),
    path('api/map_pools/<int:map_pool_id>/map/<int:map_id>/position/', UpdateMapPosition.as_view(),
         name='update-map-position'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(router.urls)),
    path('api/users/login/', UserLogin.as_view(), name='login'),
    path('api/users/logout/', views.logout_view, name='logout'),
]
