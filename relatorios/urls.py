from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('rel_funcionarios/', views.rel_funcionarios, name='rel_funcionarios'),
]