from django.urls import path
from . import views

urlpatterns = [
    path('composition/', views.JigCompositionView.as_view(), name='jig_composition'),
]