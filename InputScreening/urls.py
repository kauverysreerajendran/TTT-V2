from django.urls import path
from .views import *

urlpatterns = [
    path('IS_PickTable/', IS_PickTable.as_view(), name='IS_PickTable'),
    path('IS_RejectTable/', IS_RejectTable.as_view(), name='IS_RejectTable'),
    path('save_ip_pick_remark/', SaveIPPickRemarkAPIView.as_view(), name='save_ip_pick_remark'),
    path('save_ip_checkbox/', SaveIPCheckboxView.as_view(), name='save_ip_checkbox'),
    path('is_accepted_form/', IS_Accepted_form.as_view(), name='is_accepted_form'),
    path('batch_rejection/', BatchRejectionAPIView.as_view(), name='batch_rejection'),
    path('tray_rejection/', TrayRejectionAPIView.as_view(), name='tray_rejection'),
    path('reject_check_tray_id/', reject_check_tray_id, name='reject_check_tray_id'),
    path('get_accepted_tray_scan_data/', get_accepted_tray_scan_data, name='get_accepted_tray_scan_data'),
    path('save_accepted_tray_scan/', save_accepted_tray_scan, name='save_accepted_tray_scan'),
    path('check_tray_id/', check_tray_id, name='check_tray_id'),
    path('ip_delete_batch/', IPDeleteBatchAPIView.as_view(), name='ip_delete_batch'),
    path('IS_AcceptTable/', IS_AcceptTable.as_view(), name='IS_AcceptTable'),
    path('IS_Completed_Table/', IS_Completed_Table.as_view(), name='IS_Completed_Table'),
    path('ip_update_batch_quantity/', IPUpdateBatchQuantityAPIView.as_view(), name='ip_update_batch_quantity'),
    
# Recovery IS URLs
    path('Recovery_IS_PickTable/', Recovery_IS_PickTable.as_view(), name='Recovery_IS_PickTable'),
    path('Recovery_IS_Completed_Table/', Recovery_IS_Completed_Table.as_view(), name='Recovery_IS_Completed_Table'),
    path('Recovery_IS_AcceptTable/', Recovery_IS_AcceptTable.as_view(), name='Recovery_IS_AcceptTable'),
    path('Recovery_IS_RejectTable/', Recovery_IS_RejectTable.as_view(), name='Recovery_IS_RejectTable'),

]