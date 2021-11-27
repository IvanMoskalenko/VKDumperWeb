from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('active_process', views.active_process, name='active_process')
]
