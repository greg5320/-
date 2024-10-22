from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.db import models


class Map(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('active', 'Действует'), ('deleted', 'Удалён')], default='active')
    image_url = models.URLField(max_length=500)
    players = models.CharField(max_length=50)
    tileset = models.CharField(max_length=50)
    overview = models.TextField()

    def __str__(self):
        return self.title


class MapPool(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('submitted', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    player_login = models.CharField(max_length=150, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    submit_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='map_pools')
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='moderated_map_pools')

    def __str__(self):
        return f"MapPool {self.id} - {self.status}"


class MapMapPool(models.Model):
    map_pool = models.ForeignKey(MapPool, related_name='mapmappool', on_delete=models.CASCADE)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['map_pool', 'map'], name='unique_map_pool_map')
        ]

    def __str__(self):
        return f"Map {self.map.title} in MapPool {self.map_pool.id} (Position: {self.position})"


'''
class NewUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=50, verbose_name="Пароль")
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)
    USERNAME_FIELD = 'email'

    objects = NewUserManager()
'''
