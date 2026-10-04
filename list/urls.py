"""URL routes for the task list app."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('focus/', views.focus, name='focus'),
    path('tasks/', views.item_list, name='item_list'),
    path('tasks/add/', views.item_create, name='item_create'),
    path('tasks/<int:pk>/', views.item_detail, name='item_detail'),
    path('tasks/<int:pk>/edit/', views.item_update, name='item_update'),
    path('tasks/<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('tasks/<int:pk>/toggle/', views.item_toggle, name='item_toggle'),
]
