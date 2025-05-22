# Day_Planning/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='day_planning_home'),
    path('pick-table/', views.dp_pick_table, name='dp_pick_table'),

]
