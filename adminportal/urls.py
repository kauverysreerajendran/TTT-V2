from django.urls import path
from .views import *

urlpatterns = [
    path('Table/',Table.as_view(),name="Table"),

]