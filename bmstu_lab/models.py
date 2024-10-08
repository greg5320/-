from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

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
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_map_pools')

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

class AuthUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    is_moderator = models.BooleanField(default=False, verbose_name='Is Moderator')
    is_creator = models.BooleanField(default=False, verbose_name='Is Creator')

    def __str__(self):
        return self.username
