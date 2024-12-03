from collections import OrderedDict

from rest_framework import serializers
from rest_framework.authtoken.admin import User

from .models import Map, MapPool, MapMapPool


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

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class MapMapPoolSerializer(serializers.ModelSerializer):
    map = MapSerializer()
    position = serializers.IntegerField(min_value=1)

    class Meta:
        model = MapMapPool
        fields = ['map', 'position']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class MapPoolSerializer(serializers.ModelSerializer):
    user_login = serializers.CharField(source='user.username', read_only=True)
    moderator_login = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    maps = MapMapPoolSerializer(source='mapmappool', many=True, read_only=True)

    class Meta:
        model = MapPool
        fields = ['id', 'status', 'player_login', 'popularity', 'creation_date', 'submit_date', 'complete_date',
                  'user_login',
                  'moderator_login', 'maps']
        read_only_fields = ['user_login', 'moderator_login', 'creation_date', 'submit_date', 'complete_date',
                            'popularity']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'is_staff']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

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

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff', 'is_superuser']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class DraftSerializer(serializers.Serializer):
    map_id = serializers.IntegerField(default=1)


class PlayerLoginSerializer(serializers.Serializer):
    player_login = serializers.CharField()


class CompleteSerializer(serializers.Serializer):
    action = serializers.CharField(default="complete")


class MapFilterSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)


class MapPoolFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, help_text="Дата начала для фильтрации (в формате ГГГГ-ММ-ДД).")
    end_date = serializers.DateField(required=False, help_text="Дата окончания для фильтрации (в формате ГГГГ-ММ-ДД).")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
