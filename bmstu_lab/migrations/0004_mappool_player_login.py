# Generated by Django 5.1.1 on 2024-10-01 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmstu_lab', '0003_remove_mapcart_cart_remove_mapcart_map_mappool_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mappool',
            name='player_login',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
