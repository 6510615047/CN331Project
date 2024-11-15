from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import User, Folder, Highscore, Word

admin.site.register(User)
admin.site.register(Folder)
admin.site.register(Highscore)
admin.site.register(Word)