from django.urls import path
from . import views


urlpatterns = [
    path('help_center/', views.help_center, name='help_center'),
]