# Generated by Django 5.1.1 on 2024-11-23 07:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wordguess', '0002_remove_wordguessgame_attempts_left_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WordGuessGame',
        ),
    ]