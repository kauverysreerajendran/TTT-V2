from django.urls import path
from .views import *

urlpatterns = [
    path('BulkUpload/',BulkUpload.as_view(),name="BulkUpload"),
    path('', IndexView.as_view(), name='day_planning_home'),
    path('pick-table/', DPPickTableView.as_view(), name='dp_pick_table'),
]