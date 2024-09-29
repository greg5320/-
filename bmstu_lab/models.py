from django.db import models
from django.contrib.auth.models import User

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
    creation_date = models.DateTimeField(auto_now_add=True)
    submit_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_pools')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_map_pools')

    def __str__(self):
        return f"MapPool {self.id} - {self.status}"

class MapMapPool(models.Model):
    map_pool = models.ForeignKey(MapPool, on_delete=models.CASCADE)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    #quantity = models.PositiveIntegerField(default=1)
    position = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['map_pool', 'map'], name='unique_map_pool_map')
        ]

    def __str__(self):
        return f"Map {self.map.title} in MapPool {self.map_pool.id} (Position: {self.position})"
