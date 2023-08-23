from django.urls import path
from mpc import views

app_name='mpc'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('publicacao/<str:coDemandante>', views.publicacao, name='publicacao'),
    path('save_publicacao/', views.save_publicacao, name='save_publicacao'),
    path('delete_publicacao/', views.delete_publicacao, name='delete_publicacao'),
]
