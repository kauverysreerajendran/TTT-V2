from django.urls import path
from .views import *

urlpatterns = [
    path('bulk_upload/', DPBulkUploadView.as_view(), name='bulk_upload'),
    path('bulk_upload/preview/', DPBulkUploadPreviewView.as_view(), name='bulk_upload_preview'),
    path('dp_pick_table/', DayPlanningPickTableAPIView.as_view(), name='dp_pick_table'),
    path('tray_scan/', TrayIdScanAPIView.as_view(), name='tray_scan_api'),
    path('tray_id_list/', TrayIdListAPIView.as_view(), name='tray_id_list'),
    path('tray_id_unique_check/', TrayIdUniqueCheckAPIView.as_view(), name='tray_id_unique_check'),
    path('draft_tray/', DraftTrayIdAPIView.as_view(), name='draft_tray'),
    path('draft_tray_id_list/', DraftTrayIdListAPIView.as_view(), name='draft_tray_id_list'),
    path('dp_completed_table/', DPCompletedTableView.as_view(), name='dp_completed_table'),  # <-- Add this
    path('delete_batch/', DeleteBatchAPIView.as_view(), name='delete_batch'),
    path('update_batch_quantity/', UpdateBatchQuantityAPIView.as_view(), name='update_batch_quantity'),
    path('save_dp_pick_remark/', SaveDPPickRemarkAPIView.as_view(), name='save_dp_pick_remark'),

]