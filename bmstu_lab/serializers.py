from rest_framework import serializers
from .models import Map, MapPool, MapMapPool
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

class MapMapPoolSerializer(serializers.ModelSerializer):

    map = MapSerializer()
    position = serializers.IntegerField(min_value=1)

    class Meta:
        model = MapMapPool
        fields = ['map', 'position']

class MapPoolSerializer(serializers.ModelSerializer):
    user_login = serializers.CharField(source='user.username', read_only=True)
    moderator_login = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    maps = MapMapPoolSerializer(source='mapmappool', many=True, read_only=True)
    class Meta:
        model = MapPool
        fields = ['id', 'status', 'player_login', 'creation_date', 'submit_date', 'complete_date', 'user_login', 'moderator_login','maps']
        read_only_fields = ['user_login','moderator_login', 'creation_date', 'submit_date', 'complete_date']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'is_staff']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=validated_data.get('is_staff', False),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']