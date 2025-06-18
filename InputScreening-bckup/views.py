from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from modelmasterapp.models import *  # Import the TrayId model
from rest_framework.views import APIView
from rest_framework.response import Response
from modelmasterapp.models import *
from modelmasterapp.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.db.models import OuterRef, Subquery
import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
import math
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db.models import F
from django.core.paginator import Paginator
from django.templatetags.static import static
from django.contrib.auth.decorators import login_required
from rest_framework import status
from django.db.models import Exists
import traceback   
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from django.db.models import OuterRef, Subquery, Exists

class IS_PickTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_PickTable.html'

    def get(self, request, *args, **kwargs):
        user = request.user

        # Subqueries for annotations
        last_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('last_process_module')[:1]
        next_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('next_process_module')[:1]
        lot_id_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('lot_id')[:1] 
        dp_missing_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_missing_qty')[:1]
        dp_physical_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty')[:1]
        dp_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty_edited')[:1]

        accepted_ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_Ip_stock')[:1]
        

        ip_rejection_reasons = IP_Rejection_Table.objects.select_related('group').all()
        
        # Dynamically assign colors to each group name
        group_names = IP_RejectionGroup.objects.values_list('group_name', flat=True)
        color_palette = [
            "#e53935",  # red
            "#fb8c00",  # orange
            "#43a047",  # green
            "#1e88e5",  # blue
            "#8e24aa",  # purple
            "#fbc02d",  # yellow
            "#00897b",  # teal
            "#6d4c41",  # brown
            "#757575",  # grey
            "#3949ab",  # indigo
        ]
        group_color_map = {}
        for idx, name in enumerate(group_names):
            group_color_map[name] = color_palette[idx % len(color_palette)]

        # Annotate each reason with its color
        for reason in ip_rejection_reasons:
            group_name = reason.group.group_name if reason.group else ""
            reason.row_color = group_color_map.get(group_name, "#222")  # default dark gray

        
        ip_person_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_person_qty_verified')[:1]
        
        rejected_ip_stock_subquery = TotalStockModel.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('rejected_ip_stock')[:1]
        
        few_cases_accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('few_cases_accepted_Ip_stock')[:1]
        
        accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('accepted_tray_scan_status')[:1]
        
        IP_pick_remarks_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('IP_pick_remarks')[:1]


        # Only include ModelMasterCreation with a related TotalStockModel with tray_scan_status=True
        tray_scan_exists = Exists(
            TotalStockModel.objects.filter(
                batch_id=OuterRef('pk'),
                tray_scan_status=True
            )
        )
        

        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0
        ).annotate(
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            wiping_required=F('model_stock_no__wiping_required'),
            tray_scan_exists=tray_scan_exists,
            stock_lot_id=Subquery(lot_id_subquery),  # <-- Add this line
            ip_person_qty_verified=Subquery(ip_person_qty_verified_subquery),
            dp_missing_qty=Subquery(dp_missing_qty_subquery),
            dp_physical_qty=Subquery(dp_physical_qty_subquery),
            accepted_Ip_stock=Subquery(accepted_ip_stock_subquery),
            rejected_ip_stock=Subquery(rejected_ip_stock_subquery),
            few_cases_accepted_Ip_stock=(few_cases_accepted_Ip_stock_subquery),
            accepted_tray_scan_status=Subquery(accepted_tray_scan_status_subquery),
            IP_pick_remarks=Subquery(IP_pick_remarks_subquery),
            dp_physical_qty_edited=Subquery(dp_physical_qty_edited_subquery),


        ).filter(tray_scan_exists=True)

        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page_number)

        master_data = list(page_obj.object_list.values(
            'batch_id',
            'date_time',
            'model_stock_no__model_no',
            'plating_color',
            'polish_finish',
            'version__version_name',
            'vendor_internal',
            'location__location_name',
            'no_of_trays',
            'tray_type',
            'total_batch_quantity',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'wiping_required',
            'stock_lot_id',
            'ip_person_qty_verified',
            'dp_missing_qty',
            'dp_physical_qty',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
            'dp_physical_qty_edited',
            
        ))  

        for data in master_data:
            total_batch_quantity = data.get('total_batch_quantity', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(total_batch_quantity / tray_capacity)
            else:
                data['no_of_trays'] = 0
                
            # Get the ModelMasterCreation instance
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc:
                # Get images from related ModelMaster (model_stock_no)
                model_master = mmc.model_stock_no
                for img in model_master.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            # If no images, add a placeholder
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images
            
             # --- Add available_qty for each row ---
            lot_id = data.get('stock_lot_id')
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                if total_stock_obj.rejected_ip_stock and total_stock_obj.dp_physical_qty > 0:
                    data['available_qty'] = total_stock_obj.dp_physical_qty
                else:
                    data['available_qty'] = total_stock_obj.total_stock
            else:
                data['available_qty'] = 0
            
        

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'ip_rejection_reasons': ip_rejection_reasons,  # <-- add this line

        }
        return Response(context, template_name=self.template_name)



@method_decorator(csrf_exempt, name='dispatch')
class SaveIPPickRemarkAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            remark = data.get('remark', '').strip()
            if not batch_id:
                return JsonResponse({'success': False, 'error': 'Missing batch_id'}, status=400)
            mmc = ModelMasterCreation.objects.filter(batch_id=batch_id).first()
            if not mmc:
                return JsonResponse({'success': False, 'error': 'Batch not found'}, status=404)
            batch_obj = TotalStockModel.objects.filter(batch_id=mmc).first()
            if not batch_obj:
                return JsonResponse({'success': False, 'error': 'TotalStockModel not found'}, status=404)
            batch_obj.IP_pick_remarks = remark
            batch_obj.save(update_fields=['IP_pick_remarks'])
            return JsonResponse({'success': True, 'message': 'Remark saved'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')  
class SaveIPCheckboxView(APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            lot_id = data.get("lot_id")
            missing_qty = data.get("missing_qty")

            if not lot_id:
                return Response({"success": False, "error": "Lot ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock.ip_person_qty_verified = True

            if missing_qty not in [None, ""]:
                try:
                    missing_qty = int(missing_qty)
                except ValueError:
                    return Response({"success": False, "error": "Missing quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

                if missing_qty > total_stock.total_stock:
                    return Response(
                        {"success": False, "error": "Missing quantity must be less than or equal to assigned quantity."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Save missing qty and physical qty
                total_stock.dp_missing_qty = missing_qty
                total_stock.dp_physical_qty = total_stock.total_stock - missing_qty

            total_stock.save()
            return Response({"success": True})

        except TotalStockModel.DoesNotExist:
            return Response({"success": False, "error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            traceback.print_exc()   
            return Response({"success": False, "error": "Unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request, format=None):
        return Response(
            {"success": False, "error": "Invalid request method."},
            status=status.HTTP_400_BAD_REQUEST
        )
        


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class IS_Accepted_form(APIView):

    def post(self, request, format=None):
        data = request.data
        lot_id = data.get("stock_lot_id")
        try:
            total_stock_data = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock_data.accepted_Ip_stock = True
    
            # Use dp_physical_qty if set and > 0, else use total_stock
            physical_qty = total_stock_data.dp_physical_qty
            if not physical_qty or physical_qty == 0:
                physical_qty = total_stock_data.total_stock
    
            total_stock_data.total_IP_accpeted_quantity = physical_qty
    
            # Update process modules
            total_stock_data.next_process_module = "Brass QC"
            total_stock_data.last_process_module = "Input screening"
            total_stock_data.save()
            return Response({"success": True})
        
        except TotalStockModel.DoesNotExist:
            return Response(
                {"success": False, "error": "Stock not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BatchRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            lot_id = data.get('lot_id')  # <-- get lot_id from POST
            total_qty = data.get('total_qty', 0)

            # Get ModelMasterCreation by batch_id string
            mmc = ModelMasterCreation.objects.filter(batch_id=batch_id).first()
            if not mmc:
                return Response({'success': False, 'error': 'Batch not found'}, status=404)

            # Get TotalStockModel using lot_id (not batch_id)
            total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Get dp_physical_qty if set and > 0, else use total_stock
            qty = total_stock.dp_physical_qty if total_stock.dp_physical_qty and total_stock.dp_physical_qty > 0 else total_stock.total_stock

            # Set rejected_ip_stock = True
            total_stock.rejected_ip_stock = True
            total_stock.save(update_fields=['rejected_ip_stock'])

            # Create IP_Rejection_ReasonStore entry
            IP_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=qty,
                batch_rejection=True
            )

            return Response({'success': True, 'message': 'Batch rejection saved.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TrayRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            batch_id = data.get('batch_id')
            tray_rejections = data.get('tray_rejections', [])  # List of {reason_id, qty, tray_id}

            if not lot_id or not tray_rejections:
                return Response({'success': False, 'error': 'Missing lot_id or tray_rejections'}, status=400)

            # Get the TotalStockModel for this lot_id
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock_obj:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Use rejected_ip_stock if set and > 0, else use total_stock
            available_qty = total_stock_obj.total_stock
            if total_stock_obj.rejected_ip_stock and total_stock_obj.dp_physical_qty > 0:
                available_qty = total_stock_obj.dp_physical_qty

            # Calculate the running total and check for exceeding
            running_total = 0
            for idx, item in enumerate(tray_rejections):
                qty = int(item.get('qty', 0))
                running_total += qty
                if running_total > available_qty:
                    return Response({
                        'success': False,
                        'error': f'Quantity exceeds available ({available_qty}).'
                    }, status=400)

            # Validate all tray_ids exist in TrayId table
            for item in tray_rejections:
                tray_id = item.get('tray_id')
                if tray_id and not TrayId.objects.filter(tray_id=tray_id).exists():
                    return Response({'success': False, 'error': f'Tray ID "{tray_id}" is not existing.'}, status=400)

            # 1. Save to IP_Rejection_ReasonStore (all reasons for this lot)
            reason_ids = [item['reason_id'] for item in tray_rejections if int(item['qty']) > 0]
            reasons = IP_Rejection_Table.objects.filter(rejection_reason_id__in=reason_ids)
            total_qty = sum(int(item['qty']) for item in tray_rejections if int(item['qty']) > 0)
            reason_store = IP_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=total_qty,
                batch_rejection=False
            )
            reason_store.rejection_reason.set(reasons)

            # 2. Save each tray scan to IP_Rejected_TrayScan
            for item in tray_rejections:
                qty = int(item['qty'])
                if qty > 0:
                    reason_obj = IP_Rejection_Table.objects.get(rejection_reason_id=item['reason_id'])
                    IP_Rejected_TrayScan.objects.create(
                        lot_id=lot_id,
                        rejected_tray_quantity=qty,
                        rejection_reason=reason_obj,
                        user=request.user,
                        rejected_tray_id=item.get('tray_id', '')
                    )
            # --- Set few_cases_accepted_Ip_stock = True ---
            total_stock_obj.few_cases_accepted_Ip_stock = True
            total_stock_obj.save(update_fields=['few_cases_accepted_Ip_stock'])


            return Response({'success': True, 'message': 'Tray rejections saved.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

from django.views.decorators.http import require_GET

@require_GET
def reject_check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    exists = TrayId.objects.filter(tray_id=tray_id).exists()
    return JsonResponse({'exists': exists})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accepted_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        tray_id_store_qs = IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id)
        tray_id_store_data = [
            {
                'lot_id': obj.lot_id,
                'tray_id': obj.tray_id,
                'tray_qty': obj.tray_qty,
                'user': obj.user.username if obj.user else None,
            }
            for obj in tray_id_store_qs
        ]

        # Get model_no and tray_capacity from TotalStockModel
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        model_no = ""
        tray_capacity = 0
        total_stock = 0
        if stock:
            model_no = stock.model_stock_no.model_no if stock.model_stock_no else ""
            tray_capacity = stock.batch_id.tray_capacity if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 0
            # Use dp_physical_qty if set and > 0, else use total_stock
            if stock.dp_physical_qty and stock.dp_physical_qty > 0:
                total_stock = stock.dp_physical_qty
            else:
                total_stock = stock.total_stock or 0

        # Get total rejection quantity for this lot
        total_rejection_qty = 0
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        if reason_store:
            total_rejection_qty = reason_store.total_rejection_quantity

        # Calculate remaining stock for acceptance
        remaining_qty = total_stock - total_rejection_qty

        # If no accepted tray rows, generate rows based on remaining_qty and tray_capacity
        if not tray_id_store_data and stock and tray_capacity > 0 and remaining_qty > 0:
            from math import ceil
            qty_left = remaining_qty
            tray_id_store_data = []
            for i in range(ceil(remaining_qty / tray_capacity)):
                qty = tray_capacity if qty_left > tray_capacity else qty_left
                tray_id_store_data.append({
                    'lot_id': lot_id,
                    'tray_id': '',
                    'tray_qty': qty,
                    'user': None,
                    'sno': i + 1,
                })
                qty_left -= qty

        # Add S.no for frontend
        for idx, row in enumerate(tray_id_store_data):
            row['sno'] = idx + 1

        return Response({
            'success': True,
            'rows': tray_id_store_data,
            'model_no': model_no,
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_accepted_tray_scan(request):
    try:
        data = request.data
        lot_id = data.get('lot_id')
        rows = data.get('rows', [])
        user = request.user

        if not lot_id or not rows:
            return Response({'success': False, 'error': 'Missing lot_id or rows'}, status=400)

        # Validate all tray_ids exist in TrayId table
        for idx, row in enumerate(rows):
            tray_id = row.get('tray_id')
            if not tray_id or not TrayId.objects.filter(tray_id=tray_id).exists():
                return Response({
                    'success': False,
                    'error': f'Tray ID "{tray_id}" is not existing (Row {idx+1}).'
                }, status=400)

        # Remove existing tray IDs for this lot (optional: to avoid duplicates)
        IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).delete()

        total_qty = 0
        for row in rows:
            tray_id = row.get('tray_id')
            tray_qty = row.get('tray_qty')
            if not tray_id or tray_qty is None:
                continue
            total_qty += int(tray_qty)
            IP_Accepted_TrayID_Store.objects.create(
                lot_id=lot_id,
                tray_id=tray_id,
                tray_qty=tray_qty,
                user=user
            )

        # Save/Update IP_Accepted_TrayScan for this lot
        accepted_scan, created = IP_Accepted_TrayScan.objects.get_or_create(
            lot_id=lot_id,
            user=user,
            defaults={'accepted_tray_quantity': total_qty}
        )
        if not created:
            accepted_scan.accepted_tray_quantity = total_qty
            accepted_scan.save(update_fields=['accepted_tray_quantity'])

        # Optionally, update TotalStockModel flags
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if stock:
            stock.accepted_tray_scan_status = True
            stock.next_process_module = "Brass QC"
            stock.last_process_module = "Input screening"
            stock.save(update_fields=['accepted_tray_scan_status', 'next_process_module', 'last_process_module'])

        return Response({'success': True, 'message': 'Accepted tray scan saved.'})

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@require_GET
def check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    lot_id = request.GET.get('lot_id', '')  # This is your stock_lot_id

    # 1. Must exist in TrayId table and lot_id must match
    tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
    exists = bool(tray_obj)
    same_lot = exists and str(tray_obj.lot_id) == str(lot_id)

    # 2. Must NOT be in IP_Rejected_TrayScan for this lot
    already_rejected = False
    if exists and same_lot and lot_id:
        already_rejected = IP_Rejected_TrayScan.objects.filter(
            lot_id=lot_id,
            rejected_tray_id=tray_id
        ).exists()

    # Only valid if exists, same lot, and not already rejected
    is_valid = exists and same_lot and not already_rejected

    return JsonResponse({
        'exists': is_valid,
        'already_rejected': already_rejected,
        'not_in_same_lot': exists and not same_lot
    })

from django.db.models import Q

class IS_RejectTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_RejectTable.html'

    def get(self, request):
        # Show rows where rejected_ip_stock=True OR few_cases_accepted_Ip_stock=True
        rejected_stocks = TotalStockModel.objects.filter(
            Q(rejected_ip_stock=True) | Q(few_cases_accepted_Ip_stock=True)
        )
        master_data = []
        for idx, stock in enumerate(rejected_stocks, 1):
            mmc = stock.batch_id
            reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=stock.lot_id).order_by('-id').first()
            reasons = []
            
            if reason_store:
                for reason in reason_store.rejection_reason.all():
                    tray_scans = IP_Rejected_TrayScan.objects.filter(
                        lot_id=stock.lot_id,
                        rejection_reason=reason
                    )
                    total_tray_qty = sum(int(ts.rejected_tray_quantity) for ts in tray_scans if str(ts.rejected_tray_quantity).isdigit())
                    reasons.append({
                        "letter": reason.rejection_reason_id or "",
                        "color": reason.group.row_color if reason.group and hasattr(reason.group, "row_color") else "#888",
                        "text": reason.rejection_reason,
                        "qty": reason.rejection_count,
                        "rejected_tray_quantity": total_tray_qty,
                    })
            print("Lot:", stock.lot_id, "Reasons:", reasons)
            # Calculate no_of_trays based on reject_quantity and tray_capacity
            reject_quantity = reason_store.total_rejection_quantity if reason_store else 0
            tray_capacity = mmc.tray_capacity if mmc and hasattr(mmc, 'tray_capacity') and mmc.tray_capacity else 1
            if tray_capacity > 0:
                no_of_trays = math.ceil(reject_quantity / tray_capacity)
            else:
                no_of_trays = 0

            master_data.append({
                "sno": idx,
                "date_time": mmc.date_time.strftime("%Y-%m-%d %I:%M %p") if mmc else "",
                "model_stock_no": mmc.model_stock_no.model_no if mmc and mmc.model_stock_no else "",
                "plating_color": mmc.plating_color if mmc else "",
                "polish_finish": mmc.polish_finish if mmc else "",
                "version": mmc.version.version_name if mmc and mmc.version else "",
                "vendor_location": f"{mmc.vendor_internal}_{mmc.location.location_name}" if mmc and mmc.location else "",
                "tray_type_capacity": f"{mmc.tray_type} {mmc.tray_capacity}" if mmc else "",
                "no_of_trays": no_of_trays,
                "reject_quantity": reject_quantity,
                "reasons": reasons,  # Each reason now has 'text' and 'rejected_tray_quantity'
                "model_images": [img.master_image.url for img in mmc.model_stock_no.images.all()] if mmc and mmc.model_stock_no else [],
                "lot_id": stock.lot_id,
            })
        return Response({"master_data": master_data}, template_name=self.template_name)


@method_decorator(csrf_exempt, name='dispatch')
class IPDeleteBatchAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            stock_lot_id = data.get('stock_lot_id')
            if not stock_lot_id:
                return JsonResponse({'success': False, 'error': 'Missing stock_lot_id'}, status=400)
            obj = TotalStockModel.objects.filter(lot_id=stock_lot_id).first()
            if not obj:
                return JsonResponse({'success': False, 'error': 'Stock lot not found'}, status=404)
            obj.delete()
            return JsonResponse({'success': True, 'message': 'Stock lot deleted'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class IPUpdateBatchQuantityAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            new_quantity = data.get('dp_physical_qty')
            if not batch_id or new_quantity is None:
                return JsonResponse({'success': False, 'error': 'Missing batch_id or quantity'}, status=400)
            # Find the TotalStockModel for this batch
            stock_obj = TotalStockModel.objects.filter(batch_id__batch_id=batch_id).first()
            if not stock_obj:
                return JsonResponse({'success': False, 'error': 'Stock not found for this batch'}, status=404)
            stock_obj.dp_physical_qty = new_quantity
            stock_obj.dp_physical_qty_edited = True  # <-- Set the flag here
            stock_obj.save(update_fields=['dp_physical_qty', 'dp_physical_qty_edited'])
            return JsonResponse({'success': True, 'message': 'Quantity updated'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

class IS_AcceptTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_AcceptTable.html'

    def get(self, request):
        user = request.user

        # Only include ModelMasterCreation with a related TotalStockModel with accepted_Ip_stock=True
        accepted_exists = Exists(
            TotalStockModel.objects.filter(
                batch_id=OuterRef('pk'),
                accepted_Ip_stock=True
            )
        )

        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0
        ).annotate(
            last_process_module=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('last_process_module')[:1]
            ),
            next_process_module=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('next_process_module')[:1]
            ),
            wiping_required=F('model_stock_no__wiping_required'),
            accepted_exists=accepted_exists,
            stock_lot_id=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('lot_id')[:1]
            ),
            ip_person_qty_verified=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('ip_person_qty_verified')[:1]
            ),
            dp_missing_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('dp_missing_qty')[:1]
            ),
            dp_physical_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('dp_physical_qty')[:1]
            ),
            accepted_Ip_stock=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('accepted_Ip_stock')[:1]
            ),
            rejected_ip_stock=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('rejected_ip_stock')[:1]
            ),
            few_cases_accepted_Ip_stock=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('few_cases_accepted_Ip_stock')[:1]
            ),
            accepted_tray_scan_status=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('accepted_tray_scan_status')[:1]
            ),
            IP_pick_remarks=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('IP_pick_remarks')[:1]
            ),
            total_IP_accpeted_quantity=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('total_IP_accpeted_quantity')[:1]
            ),
            
        ).filter(accepted_exists=True)
        

        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page_number)

        master_data = list(page_obj.object_list.values(
            'batch_id',
            'date_time',
            'model_stock_no__model_no',
            'plating_color',
            'polish_finish',
            'version__version_name',
            'vendor_internal',
            'location__location_name',
            'no_of_trays',
            'tray_type',
            'total_IP_accpeted_quantity',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'wiping_required',
            'stock_lot_id',
            'ip_person_qty_verified',
            'dp_missing_qty',
            'dp_physical_qty',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
        ))

        for data in master_data:
            total_IP_accpeted_quantity = data.get('total_IP_accpeted_quantity', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(total_IP_accpeted_quantity / tray_capacity)
            else:
                data['no_of_trays'] = 0

            # Get the ModelMasterCreation instance
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc:
                model_master = mmc.model_stock_no
                for img in model_master.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images

            # Add available_qty for each row
            lot_id = data.get('stock_lot_id')
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                if total_stock_obj.rejected_ip_stock and total_stock_obj.dp_physical_qty > 0:
                    data['available_qty'] = total_stock_obj.dp_physical_qty
                else:
                    data['available_qty'] = total_stock_obj.total_stock
            else:
                data['available_qty'] = 0

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
        }
        return Response(context, template_name=self.template_name)
    
class IS_Completed_Table(APIView):
    def get(self, request):
        return render(request, 'Input_Screening/IS_Completed_Table.html')

# Recovery Input Screening Views
class Recovery_IS_PickTable(APIView):
    def get(self, request):
        return render(request, 'Recovery_IS/Recovery_IS_PickTable.html')
    
class Recovery_IS_Completed_Table(APIView): 
    def get(self, request):
        return render(request, 'Recovery_IS/Recovery_IS_Completed_Table.html')
    
class Recovery_IS_AcceptTable(APIView):
    def get(self, request):
        return render(request, 'Recovery_IS/Recovery_IS_AcceptTable.html')
    
class Recovery_IS_RejectTable(APIView):
    def get(self, request):
        return render(request, 'Recovery_IS/Recovery_IS_RejectTable.html')