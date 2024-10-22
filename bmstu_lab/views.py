import uuid
from urllib.parse import urlparse

import redis
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from minio import S3Error, Minio
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Map, MapPool, MapMapPool
from .permissions import IsAdmin
from .serializers import MapSerializer, MapMapPoolSerializer, \
    MapPoolSerializer, DraftSerializer, \
    CompleteSerializer, UserUpdateSerializer, RegisterSerializer, LoginSerializer, PlayerLoginSerializer
from .utils import add_image

minio_client = Minio(settings.MINIO_STORAGE_ENDPOINT,
                     access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                     secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                     secure=settings.MINIO_STORAGE_USE_HTTPS)

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


# def get_creator():
#   return User.objects.get(username=settings.CREATOR_USERNAME)
def extract_between_quotes(data):
    # Убеждаемся, что работаем со строкой
    if isinstance(data, bytes):
        data = data.decode('utf-8')

    # Проверяем, что строка начинается и заканчивается одинарными кавычками
    if data.startswith("'") and data.endswith("'"):
        return data[1:-1]  # Убираем кавычки
    return data  # Возвращаем строку без изменений, если она не в кавычках


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)

        return decorated_func

    return decorator


class MapList(APIView):
    # permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        maps = Map.objects.filter(status='active')
        title = request.query_params.get('title')
        draft_id = None
        draft_count = None
        if title:
            maps = maps.filter(title__icontains=title)
        serializer = MapSerializer(maps, many=True)
        if real_user is not None:
            draft_map_pool = MapPool.objects.filter(user=request.user, status='draft').first()
            draft_id = draft_map_pool.id if draft_map_pool else None
            draft_count = draft_map_pool.mapmappool.count() if draft_map_pool else 0
        return Response({
            'maps': serializer.data,
            'draft_id': draft_id,
            'draft_count': draft_count
        })

    # @method_permission_classes((IsAdmin,))
    @swagger_auto_schema(request_body=MapSerializer)
    def post(self, request):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff

        if is_staff == False:
            return Response({'status': 'error', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MapSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MapDetail(APIView):
    # permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id):
        try:
            map_obj = Map.objects.get(id=id, status='active')
        except Map.DoesNotExist:
            return Response({"Данной карты не существует"})
        serializer = MapSerializer(map_obj)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=MapSerializer)
    @method_permission_classes((IsAdmin,))
    def put(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff

        if is_staff == False:
            return Response({'status': 'error', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        map_obj = get_object_or_404(Map, id=id)
        serializer = MapSerializer(map_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAdmin,))
    def delete(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff

        if is_staff == False:
            return Response({'status': 'error', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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

    @swagger_auto_schema(request_body=DraftSerializer)
    @csrf_exempt
    def post(self, request):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff

        serializer = DraftSerializer(data=request.data)
        map_id = request.data.get('map_id')
        if not map_id:
            return Response({"error": "Нет map_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            map_obj = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            return Response({"error": "Карта не найдена"}, status=status.HTTP_404_NOT_FOUND)
        map_pool = MapPool.objects.filter(user=user, status='draft').order_by('-creation_date').first()
        if not map_pool:
            map_pool = MapPool.objects.create(
                status='draft',
                player_login=None,
                creation_date=timezone.now(),
                complete_date=None,
                user=real_user,
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
    @method_permission_classes((IsAuthenticated,))
    def get(self, request):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        map_pools = MapPool.objects.exclude(status__in=['deleted', 'draft'])
        if is_staff == False:
            map_pools = map_pools.filter(user=user)
            # map_pools = MapPool.objects.all()
        status_filter = request.query_params.get('status', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if status_filter:
            map_pools = map_pools.filter(status=status_filter)

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            map_pools = map_pools.filter(submit_date__range=[start_date, end_date])

        serializer = MapPoolSerializer(map_pools, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MapPoolDetailView(APIView):
    @method_permission_classes((IsAuthenticated,))
    def get(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        map_pool = get_object_or_404(MapPool, id=id)
        if not is_staff and str(map_pool.user) != str(real_user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = MapPoolSerializer(map_pool)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=PlayerLoginSerializer)
    @method_permission_classes((IsAuthenticated,))
    def put(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not real_user:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff

        map_pool = get_object_or_404(MapPool, id=id)
        if not is_staff and str(map_pool.user) != str(real_user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        player_login = request.data.get('player_login')
        if player_login == None:
            return Response({"error": "Поле player_login не может быть пустым"}, status=status.HTTP_400_BAD_REQUEST)
        map_pool.player_login = player_login
        map_pool.save()
        serializer = MapPoolSerializer(map_pool)
        return Response(serializer.data)

    @method_permission_classes((IsAuthenticated,))
    def delete(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        try:
            map_pool = MapPool.objects.get(id=id)
            if not is_staff and map_pool.user != real_user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except MapPool.DoesNotExist:
            return Response({"error": "Заявка не найдена"}, status=status.HTTP_404_NOT_FOUND)
        if map_pool.status == 'deleted':
            return Response({"error": "Заявка уже была удалена"}, status=status.HTTP_400_BAD_REQUEST)
        map_pool.status = 'deleted'
        map_pool.complete_date = timezone.now()
        map_pool.save()
        return Response({"message": "Заявка успешно удалена"}, status=status.HTTP_200_OK)


class MapPoolSubmitView(APIView):
    @method_permission_classes((IsAuthenticated,))
    @swagger_auto_schema(request_body=MapPoolSerializer)
    def put(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        map_pool = get_object_or_404(MapPool, id=id)
        if str(map_pool.user) != str(real_user):
            return Response("Вы должны быть создателем заявки", status=status.HTTP_400_BAD_REQUEST)
        if map_pool.status != 'draft':
            return Response("Заявка уже была сформированна", status=status.HTTP_400_BAD_REQUEST)
        if map_pool.player_login == None:
            return Response("Поле player_login обязательно должно быть заполнено", status=status.HTTP_400_BAD_REQUEST)

        map_pool.submit_date = timezone.now()
        map_pool.status = "submitted"
        map_pool.save()
        serializer = MapPoolSerializer(map_pool)
        return Response(serializer.data)


class CompleteOrRejectMapPool(APIView):
    @swagger_auto_schema(request_body=CompleteSerializer)
    @csrf_exempt
    def put(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        if is_staff == False:
            return Response({'status': 'error', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            map_pool = MapPool.objects.get(id=id, status='submitted')
        except MapPool.DoesNotExist:
            return Response({"error": "Заявка не найдена или не находится в статусе ожидания модерации"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = CompleteSerializer(data=request.data)
        action = request.data.get('action')
        if action not in ['complete', 'reject']:
            return Response({"error": "Неверное действие. Ожидается 'complete' или 'reject'"},
                            status=status.HTTP_400_BAD_REQUEST)
        map_pool.moderator = user
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

    # @method_permission_classes((IsAdmin,))
    # @swagger_auto_schema(request_body=StockSerializer)
    def post(self, request, id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff

        if is_staff == False:
            return Response({'status': 'error', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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


@permission_classes([AllowAny])
class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
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


'''
class UserLogin(ObtainAuthToken):
    @swagger_auto_schema(request_body=AuthTokenSerializer)
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
'''


class UserUpdate(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(request_body=StockSerializer)
    def post(self, request):
        try:
            token = request.auth
            token.delete()
            return Response({"message": "Вы успешно вышли из системы."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateMapPosition(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=MapMapPoolSerializer)
    def put(self, request, map_pool_id, map_id):
        map_pool = get_object_or_404(MapPool, id=map_pool_id)
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        if not is_staff and str(map_pool.user) != str(real_user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        new_position = request.data.get('position')
        map_map_pool = get_object_or_404(MapMapPool, map_pool_id=map_pool_id, map_id=map_id)
        map_map_pool.position = new_position
        map_map_pool.save()
        serializer = MapMapPoolSerializer(map_map_pool)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveMapFromMapPool(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, map_pool_id, map_id):
        ssid = request.COOKIES.get("session_id")
        username = None
        real_user = None
        if ssid:
            username = session_storage.get(ssid)
            if isinstance(username, bytes):
                username = username.decode('utf-8')
            real_user = extract_between_quotes(username)
            if not username:
                return Response({"status": "error", "error": "Invalid session"}, status=status.HTTP_403_FORBIDDEN)
        is_staff = False
        if real_user:
            if real_user:
                user = User.objects.filter(username=real_user).first()
            if user:
                is_staff = user.is_staff
        map_pool = get_object_or_404(MapPool, id=map_pool_id)
        if not is_staff and str(map_pool.user) != str(real_user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        map_map_pool = get_object_or_404(MapMapPool, map_id=map_id, map_pool_id=map_pool_id)
        map_map_pool.delete()
        return Response({"message": "Карта успешно удалена из заявки."}, status=status.HTTP_204_NO_CONTENT)


'''
class UserViewSet(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

'''


class UserLogin(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
            },
        )
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                random_key = str(uuid.uuid4())
                session_storage.set(random_key, username)
                response = HttpResponse("{'status': 'ok'}")
                response.set_cookie("session_id", random_key)
                return response
            else:
                return Response({"status": "error", "error": "login failed"},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message": "login failed", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def logout_view(request):
    session_id = request.COOKIES.get("session_id")
    if session_id:
        session_storage.delete(session_id)
    logout(request)
    response = Response({'status': 'Success'})
    response.delete_cookie("session_id")
    return response
