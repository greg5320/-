from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from urllib.parse import urlparse
from minio import S3Error, Minio
from .utils import add_image
from .models import Map, MapPool, MapMapPool
from .serializers import MapSerializer, MapMapPoolSerializer, \
    MapPoolSerializer, RegisterSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status



minio_client = Minio(settings.MINIO_STORAGE_ENDPOINT,
                     access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                     secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                     secure=settings.MINIO_STORAGE_USE_HTTPS)


def get_creator():
    return User.objects.get(username=settings.CREATOR_USERNAME)

class MapList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        maps=Map.objects.filter(status = 'active')
        title = request.query_params.get('title')
        if title:
            maps = maps.filter(title__icontains=title)

        serializer = MapSerializer(maps, many=True)
        draft_map_pool = MapPool.objects.filter(user=request.user,status = 'draft').first()
        draft_id = draft_map_pool.id if draft_map_pool else None
        draft_count = draft_map_pool.mapmappool.count() if draft_map_pool else 0

        return Response({
            'maps':serializer.data,
            'draft_id':draft_id,
            'draft_count':draft_count
        })
    def post(self,request):
        serializer = MapSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MapDetail(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        try:
            map_obj = Map.objects.get(id=id, status = 'active')
        except Map.DoesNotExist:
            return Response({"Данной карты не существует"})
        serializer = MapSerializer(map_obj)
        return Response(serializer.data)

    def put(self, request, id):
        map_obj = get_object_or_404(Map,id=id)
        serializer = MapSerializer(map_obj,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        map_obj = get_object_or_404(Map, id=id)
        if map_obj.image_url:
            try:
                parsed_url = urlparse(map_obj.image_url)
                object_name = parsed_url.path.lstrip('/')
                minio_client.remove_object(settings.MINIO_STORAGE_BUCKET_NAME, object_name)
            except S3Error as e:
                return Response({'error': f"Ошибка при удалении из Minio: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        map_obj.delete()
        return Response({'message': 'Карта успешно удалена'}, status=status.HTTP_204_NO_CONTENT)


class AddMapToDraft(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        creator = get_creator()
        map_id = request.data.get('map_id')
        if not map_id:
            return Response({"error": "Нет map_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            map_obj = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            return Response({"error": "Карта не найдена"}, status=status.HTTP_404_NOT_FOUND)
        map_pool = MapPool.objects.filter(user=creator, status='draft').order_by('-creation_date').first()
        if not map_pool:
            map_pool = MapPool.objects.create(
                status='draft',
                player_login=None,
                creation_date=timezone.now(),
                complete_date=None,
                user=creator,
                submit_date=None,
                moderator=None,
            )
        if MapMapPool.objects.filter(map_pool=map_pool, map=map_obj).exists():
            return Response({'error': 'Карта уже добавлена'}, status=status.HTTP_400_BAD_REQUEST)
        current_position = MapMapPool.objects.filter(map_pool=map_pool).count() + 1
        MapMapPool.objects.create(
            map_pool=map_pool,
            map=map_obj,
            position=current_position
        )
        map_pool_serializer = MapPoolSerializer(map_pool)
        return Response({
            "message": "Карта успешно добавлена",
            "map_pool": map_pool_serializer.data
        }, status=status.HTTP_201_CREATED)

class MapPoolListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        map_pools = MapPool.objects.exclude(status__in = ['deleted','draft'])
        #map_pools = MapPool.objects.all()
        status_filter = request.query_params.get('status',None)
        start_date = request.query_params.get('start_date',None)
        end_date = request.query_params.get('end_date',None)

        if status_filter:
            map_pools = map_pools.filter(status= status_filter)

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            map_pools = map_pools.filter(submit_date__range=[start_date, end_date])

        serializer = MapPoolSerializer(map_pools, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MapPoolDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        map_pool = get_object_or_404(MapPool,id=id)
        serializer = MapPoolSerializer(map_pool)
        return Response(serializer.data)

    def put(self,request,id):
        map_pool = get_object_or_404(MapPool,id=id)
        player_login = request.data.get('player_login')
        if player_login == None:
            return Response({"error": "Поле player_login не может быть пустым"},status=status.HTTP_400_BAD_REQUEST)
        map_pool.player_login = player_login
        map_pool.save()
        serializer = MapPoolSerializer(map_pool)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            map_pool = MapPool.objects.get(id=id)
        except MapPool.DoesNotExist:
            return Response({"error": "Заявка не найдена"}, status=status.HTTP_404_NOT_FOUND)
        if map_pool.status == 'deleted':
            return Response({"error": "Заявка уже была удалена"}, status=status.HTTP_400_BAD_REQUEST)
        map_pool.status = 'deleted'
        map_pool.complete_date = timezone.now()
        map_pool.save()
        return Response({"message": "Заявка успешно удалена"}, status=status.HTTP_200_OK)

class MapPoolSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,id):
        map_pool = get_object_or_404(MapPool,id=id)
        if map_pool.user != request.user:
            return Response("Вы должны быть создателем заявки",status=status.HTTP_400_BAD_REQUEST)
        if map_pool.status != 'draft':
            return Response("Заявка уже была сформированна",status=status.HTTP_400_BAD_REQUEST)
        if map_pool.player_login == None:
            return Response("Поле player_login обязательно должно быть заполнено",status=status.HTTP_400_BAD_REQUEST)

        map_pool.submit_date = timezone.now()
        map_pool.status = "submitted"
        map_pool.save()
        serializer = MapPoolSerializer(map_pool)
        return Response(serializer.data)

class CompleteOrRejectMapPool(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            map_pool = MapPool.objects.get(id=id, status='submitted')
        except MapPool.DoesNotExist:
            return Response({"error": "Заявка не найдена или не находится в статусе ожидания модерации"}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff:
            return Response({"error": "Доступ запрещен, вы не являетесь модератором"}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get('action')
        if action not in ['complete', 'reject']:
            return Response({"error": "Неверное действие. Ожидается 'complete' или 'reject'"}, status=status.HTTP_400_BAD_REQUEST)

        map_pool.moderator = request.user
        map_pool.complete_date = timezone.now()
        if action == 'complete':
            map_pool.status = 'completed'
        elif action == 'reject':
            map_pool.status = 'rejected'

        map_pool.save()
        serializer = MapPoolSerializer(map_pool)

        return Response({
            "message": f"Заявка успешно {('завершена' if action == 'complete' else 'отклонена')}",
            "data": serializer.data
        }, status=status.HTTP_200_OK)




class UploadImageForMap(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        map_obj = get_object_or_404(Map, id=id)

        if map_obj.image_url:
            try:
                parsed_url = urlparse(map_obj.image_url)
                object_name = parsed_url.path.lstrip('/')
                minio_client.remove_object(settings.MINIO_STORAGE_BUCKET_NAME, object_name)
            except S3Error as e:
                return Response({'error': f'Ошибка в удалении старого изображения {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'Нет предоставленного изображения'}, status=status.HTTP_400_BAD_REQUEST)

        image_result = add_image(map_obj, image)
        if 'error' in image_result.data:
            return image_result

        return Response({'message': 'Изображение успешно загружено', 'image_url': map_obj.image_url},
                        status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Пользователь успешно зарегистрирован",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserLogin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            update_last_login(None, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                }
            }, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserUpdate(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.auth
            token.delete()
            return Response({"message": "Вы успешно вышли из системы."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateMapPosition(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, map_pool_id, map_id):
        new_position = request.data.get('position')
        map_map_pool = get_object_or_404(MapMapPool, map_pool_id=map_pool_id, map_id=map_id)
        map_map_pool.position = new_position
        map_map_pool.save()
        serializer = MapMapPoolSerializer(map_map_pool)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RemoveMapFromMapPool(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, map_pool_id, map_id):
        map_map_pool = get_object_or_404(MapMapPool, map_id=map_id, map_pool_id=map_pool_id)
        map_map_pool.delete()
        return Response({"message": "Карта успешно удалена из заявки."}, status=status.HTTP_204_NO_CONTENT)