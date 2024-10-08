from rest_framework import serializers
from .models import Map, MapPool, MapMapPool, AuthUser
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User

class MapSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    status = serializers.ChoiceField(choices=[('active', 'Действует'), ('deleted', 'Удалён')])
    image_url = serializers.URLField(required=False, allow_null=True)
    players = serializers.CharField(max_length=50)
    tileset = serializers.CharField(max_length=50)
    overview = serializers.CharField()
    class Meta:
        model = Map
        fields = '__all__'

class MapPoolDetailSerializer(serializers.ModelSerializer):
    maps = serializers.SerializerMethodField()

    class Meta:
        model = MapPool
        fields = '__all__'

    def get_maps(self, obj):
        map_map_pools = obj.mapmappool.select_related('map').all()
        return [{'map': MapSerializer(map_map_pool.map).data, 'position': map_map_pool.position} for map_map_pool in map_map_pools]


class MapPoolSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=MapPool.STATUS_CHOICES)
    player_login = serializers.CharField(max_length=150, required=False, allow_blank=True)
    creation_date = serializers.DateTimeField(read_only=True)
    submit_date = serializers.DateTimeField(read_only=True)
    complete_date = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    moderator = serializers.PrimaryKeyRelatedField(queryset=AuthUser.objects.all(), required=False)
    delivery_date = serializers.DateField(required=False)

    class Meta:
        model = MapPool
        fields = '__all__'

class MapMapPoolSerializer(serializers.ModelSerializer):
    map_pool = serializers.PrimaryKeyRelatedField(queryset=MapPool.objects.all())
    map = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all())
    position = serializers.IntegerField(min_value=1)

    class Meta:
        model = MapMapPool
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

class MapUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'password', 'is_moderator', 'is_creator']

    def create(self, validated_data):
        user = AuthUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user