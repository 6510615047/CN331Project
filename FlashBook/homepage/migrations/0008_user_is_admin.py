# Generated by Django 4.2.5 on 2024-12-11 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("homepage", "0007_gameplayer_publicgame_gameplayer_game_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]
