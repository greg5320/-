from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from urllib.parse import urlparse
from minio import S3Error, Minio
from .utils import add_image
from .models import Map, MapPool, MapMapPool, AuthUser
from .serializers import MapSerializer, MapMapPoolSerializer, UserSerializer, UserRegistrationSerializer, \
    MapPoolSerializer, AuthUserSerializer, MapPoolDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes



minio_client = Minio(settings.MINIO_STORAGE_ENDPOINT,
                     access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                     secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                     secure=settings.MINIO_STORAGE_USE_HTTPS)

class MapList(APIView):
    def get(self, request, *args, **kwargs):
        # Получаем все карты
        maps = Map.objects.all()
        if not maps.exists():
            return Response({'message': 'No maps found'}, status=status.HTTP_404_NOT_FOUND)

        draft_pool = MapPool.objects.filter(user=request.user, status='draft').first()
        maps_data = MapSerializer(maps, many=True).data

        return Response({
            'maps': maps_data,
            'draft_pool_id': draft_pool.id if draft_pool else None
        })

    def post(self, request, format=None):
        serializer = MapSerializer(data=request.data)
        if serializer.is_valid():
            map_obj = serializer.save()
            image = request.FILES.get("image")
            if image:
                image_result = add_image(map_obj, image)
                if 'error' in image_result.data:
                    return image_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MapDetail(APIView):
    def get(self, request, pk, format=None):
        map_obj = get_object_or_404(Map, pk=pk)
        serializer = MapSerializer(map_obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        map_obj = get_object_or_404(Map, pk=pk)
        serializer = MapSerializer(map_obj, data=request.data, partial=True)
        if 'image' in request.FILES:
            image_result = add_image(map_obj, request.FILES['image'])
            if 'error' in image_result.data:
                return image_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        map_obj = get_object_or_404(Map, pk=pk)
        if map_obj.image_url:
            try:
                parsed_url = urlparse(map_obj.image_url)
                object_name = parsed_url.path.lstrip('/')
                minio_client.remove_object(settings.MINIO_STORAGE_BUCKET_NAME, object_name)
            except S3Error as e:
                print(f"Error deleting image from Minio: {str(e)}")
        map_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddMapToDraft(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = MapMapPoolSerializer(data=request.data)
        if serializer.is_valid():
            draft_pool, created = MapPool.objects.get_or_create(user=request.user, status='draft')
            serializer.save(map_pool=draft_pool)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MapPoolListView(generics.ListAPIView):
    serializer_class = MapPoolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        #queryset = MapPool.objects.all()
        queryset = MapPool.objects.exclude(status__in=['draft', 'deleted'])
        if user.is_moderator or user.is_creator:
            return queryset

        return queryset.filter(user=user)


class MapPoolDetailView(generics.RetrieveAPIView):
    #queryset = MapPool.objects.all()
    queryset = MapPool.objects.exclude(status__in=['draft', 'deleted'])
    serializer_class = MapPoolDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


User = get_user_model()

class AuthUserCreateView(generics.CreateAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer
    permission_classes = [AllowAny]

class UserProfileUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class UserLogin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            update_last_login(None, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response(status=status.HTTP_200_OK)

class UploadImageForMap(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        map_obj = get_object_or_404(Map, pk=pk)
        if map_obj.image_url:
            try:
                parsed_url = urlparse(map_obj.image_url)
                object_name = parsed_url.path.lstrip('/')
                minio_client.remove_object(settings.MINIO_STORAGE_BUCKET_NAME, object_name)
            except S3Error as e:
                return Response({'error': f'Error deleting old image: {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

        image_result = add_image(map_obj, image)
        if 'error' in image_result.data:
            return image_result

        return Response({'message': 'Image uploaded successfully', 'image_url': map_obj.image_url},
                        status=status.HTTP_200_OK)


class MapPoolUpdateView(generics.UpdateAPIView):
    queryset = MapPool.objects.all()
    serializer_class = MapPoolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_moderator:
            return Response({'error': 'У вас нет прав для изменения этой заявки.'}, status=status.HTTP_403_FORBIDDEN)

        required_fields = ['player_login', 'status']
        for field in required_fields:
            if field not in request.data:
                return Response({'error': f'Поле {field} обязательно.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'moderator' in request.data:
            if not request.user.is_moderator:
                return Response({'error': 'У вас нет прав для изменения модератора.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class MapPoolFinalizeView(generics.UpdateAPIView):
    queryset = MapPool.objects.all()
    serializer_class = MapPoolDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_moderator:
            return Response({'error': 'У вас нет прав для завершения или отклонения заявки.'}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')

        if new_status not in ['completed', 'rejected']:
            return Response({'error': 'Статус должен быть "completed" или "rejected".'}, status=status.HTTP_400_BAD_REQUEST)

        instance.complete_date = timezone.now()
        instance.moderator = request.user
        instance.status = new_status
        instance.save()

        map_map_pools = MapMapPool.objects.filter(map_pool=instance)
        map_positions = [{'map_title': map_map.map.title, 'position': map_map.position} for map_map in map_map_pools]
        response_data = {
            'map_pool': MapPoolDetailSerializer(instance).data,
            'maps_positions': map_positions,
        }

        return Response(response_data)
class MapPoolDeleteView(generics.DestroyAPIView):
    queryset = MapPool.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user != request.user and not request.user.is_moderator:
            return Response({'error': 'У вас нет прав для удаления этой заявки.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class MapMapPoolDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        map_pool_id = kwargs.get('map_pool_id')
        position = request.data.get('position')

        if not map_pool_id or not position:
            return Response({'error': 'Необходимо указать и map_pool, и позицию.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            map_map_pool = MapMapPool.objects.get(map_pool_id=map_pool_id, position=position)
        except MapMapPool.DoesNotExist:
            return Response({'error': 'Запись не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        if map_map_pool.map_pool.user != request.user and not request.user.is_moderator:
            return Response({'error': 'У вас нет прав для удаления этой записи.'}, status=status.HTTP_403_FORBIDDEN)
        map_map_pool.delete()

        return Response({'message': 'Запись успешно удалена.'}, status=status.HTTP_204_NO_CONTENT)

class MapMapPoolUpdatePositionView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        map_pool_id = kwargs.get('map_pool_id')
        current_position = request.data.get('current_position')
        new_position = request.data.get('new_position')

        if not current_position or not new_position:
            return Response({'error': 'Необходимо указать текущую и новую позицию.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            map_map_pool = MapMapPool.objects.get(map_pool_id=map_pool_id, position=current_position)
        except MapMapPool.DoesNotExist:
            return Response({'error': 'Запись не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        if map_map_pool.map_pool.user != request.user and not request.user.is_moderator:
            return Response({'error': 'У вас нет прав для изменения этой записи.'}, status=status.HTTP_403_FORBIDDEN)

        if MapMapPool.objects.filter(map_pool_id=map_pool_id, position=new_position).exists():
            return Response({'error': 'Позиция уже занята другой картой.'}, status=status.HTTP_400_BAD_REQUEST)

        map_map_pool.position = new_position
        map_map_pool.save()

        return Response({'message': 'Позиция успешно обновлена.'}, status=status.HTTP_200_OK)