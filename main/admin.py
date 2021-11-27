"""Models registered in admin panel"""
from django.contrib import admin
from .models import Token, Config

admin.site.register(Token)
admin.site.register(Config)
