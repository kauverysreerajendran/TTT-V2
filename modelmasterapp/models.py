from django.db import models
from django.utils import timezone
from django.db.models import F
from django.core.exceptions import ValidationError
import datetime
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class ModelImage(models.Model):
  #give master_image field for mulitple image slection
    master_image = models.ImageField(upload_to='model_images/')

    def __str__(self):
        return f"Master_Image {self.id}"
    
class PolishFinishType(models.Model):
    polish_finish = models.CharField(max_length=255, unique=True, help_text="Type of polish finish")
    polish_internal = models.CharField(
        max_length=255,
        unique=True,
        default="DefaultInternal",
        help_text="Internal name of the Polish Finish"
    )

    def __str__(self):
        return self.polish_finish 
    
class Plating_Color(models.Model):
    #need choices for plating color field -dropdown field
    plating_color = models.CharField(max_length=255, unique=True, help_text="Plating color")
    plating_color_internal = models.CharField(
        max_length=10, 
        null=True,
        blank=True,
        help_text="Short internal code used in stock number (e.g., B for Black)", 
    )
    jig_unload_zone_1 = models.BooleanField(default=False, help_text="Indicates if Jig Unload Zone 1 is active")
    jig_unload_zone_2 = models.BooleanField(default=False, help_text="Indicates if Jig Unload Zone 2 is active")

    def __str__(self):
        return self.plating_color
    
        
class Version(models.Model):
    version_name = models.CharField(max_length=255, unique=True, help_text="Version name")
    version_internal = models.CharField(max_length=255, unique=True,null=True,blank=True, help_text="Version Internal")

    def __str__(self):
        return self.version_name
    
class TrayType(models.Model):
    tray_type = models.CharField(max_length=255, unique=True, help_text="Type of tray")
    tray_capacity = models.IntegerField(help_text="Number of watches the tray can hold")  
    tray_color = models.CharField(max_length=255, help_text="Color of the tray",blank=True, null=True)  

    def __str__(self):
        return self.tray_type
    
class Vendor(models.Model):
    vendor_name = models.CharField(max_length=255, unique=True, help_text="Name of the vendor")
    vendor_internal = models.CharField(max_length=255, unique=True, help_text="Internal name of the vendor")

    def __str__(self):
        return self.vendor_name

class Location(models.Model):
    location_name = models.CharField(max_length=255, unique=True, help_text="Name of the location")

    def __str__(self):
        return self.location_name
    
    
class ModelMaster(models.Model):
    # Assuming this model holds the reference data for dropdowns and auto-fetch fields
    model_no = models.CharField(max_length=100, unique=True)
    polish_finish = models.ForeignKey(PolishFinishType, on_delete=models.SET_NULL, null=True, blank=True)
    ep_bath_type = models.CharField(max_length=100)
    tray_type = models.ForeignKey(TrayType, on_delete=models.SET_NULL, null=True, blank=True)
    tray_capacity = models.IntegerField(null=True, blank=True)
    images = models.ManyToManyField(ModelImage, blank=True)  # Allows multiple images
    vendor_internal = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=100)
    gender = models.CharField(max_length=50)
    wiping_required = models.BooleanField(default=False)
 
    def __str__(self):
        return self.model_no
    
class ModelMasterCreation(models.Model):
    
    #unique_id = models.CharField(max_length=100, unique=True,null=True, blank=True) #not in use
    batch_id = models.CharField(max_length=50, unique=True)
    lot_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # <== ADD THIS LINE
    model_stock_no = models.ForeignKey(ModelMaster, related_name='model_stock_no', on_delete=models.CASCADE)
    polish_finish = models.CharField(max_length=100)
    ep_bath_type = models.CharField(max_length=100)
    plating_color=models.CharField(max_length=100,null=True,blank=True)
    tray_type = models.CharField(max_length=100)
    tray_capacity = models.IntegerField(null=True, blank=True)
    images = models.ManyToManyField(ModelImage, blank=True)  # Store multiple images
    date_time = models.DateTimeField(default=timezone.now)
    version = models.ForeignKey(Version, on_delete=models.CASCADE, help_text="Version")
    total_batch_quantity = models.IntegerField()  
    initial_batch_quantity = models.IntegerField(default=0) #not in use
    current_batch_quantity = models.IntegerField(default=0)  # not in use
    no_of_trays = models.IntegerField(null=True, blank=True)  # Calculated field
    vendor_internal = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    gender = models.CharField(max_length=50)
    sequence_number = models.IntegerField(default=0)  # Add this field
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)  # Allow null values
    Moved_to_D_Picker = models.BooleanField(default=False, help_text="Moved to D Picker")
    Onhold_picking = models.BooleanField(default=False, help_text="On Hold Picking")
    
    def save(self, *args, **kwargs):
        
        if not self.pk:  # Only set the sequence number for new instances
            last_batch = ModelMasterCreation.objects.order_by('-sequence_number').first()
            self.sequence_number = 1 if not last_batch else last_batch.sequence_number + 1
        
        # Fetch related data from ModelMaster
        model_data = self.model_stock_no
        self.polish_finish = model_data.polish_finish.polish_type if model_data.polish_finish else ''
        self.ep_bath_type = model_data.ep_bath_type
        self.tray_type = model_data.tray_type.tray_type_name if model_data.tray_type else ''
        self.vendor_internal = model_data.vendor_internal.vendor_name if model_data.vendor_internal else ''
        self.tray_capacity = model_data.tray_capacity
        self.brand = model_data.brand
        self.gender = model_data.gender



        super().save(*args, **kwargs)
        self.images.set(model_data.images.all())


    def __str__(self):
        return f"{self.model_stock_no} - {self.batch_id}"

class Location_Tracking(models.Model):
    """
    Location Tracking Model
    Based on the same location in the same model_no, we need to find the sum of all locations in the same model_no.
    """
    model_stock_no = models.ForeignKey(ModelMaster, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    total_stock_quantity = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.model_stock_no.model_no} - {self.location.location_name}"
 
 

class BatchInitialQuantity(models.Model):
    """
    Stores the initial batch quantity before stock reductions.
    """
    batch_id = models.ForeignKey("ModelMasterCreation", on_delete=models.CASCADE, help_text="Related Batch ID")
    model_stock_no = models.ForeignKey("ModelMaster", on_delete=models.CASCADE, help_text="Model Stock Number")
    version = models.ForeignKey("Version", on_delete=models.CASCADE, help_text="Version")
    initial_batch_quantity = models.IntegerField(help_text="Initial Batch Quantity")
    module_name = models.CharField(max_length=255, help_text="Module Name")
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who recorded the batch")

    class Meta:
        unique_together = ("batch_id", "created_at")  # ✅ Ensures unique batch per timestamp

    def __str__(self):
        return f"Batch: {self.batch_id.batch_id} | Model: {self.model_stock_no.model_no} | Version: {self.version.version_name} | Initial Qty: {self.initial_batch_quantity} | User: {self.user} | Created: {self.created_at}"
   
        
class TrayId(models.Model):
    """
    TrayId Model
    Represents a tray identifier in the Titan Track and Traceability system.
   
    """
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True, help_text="Tray ID")
    tray_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    batch_id = models.ForeignKey(ModelMasterCreation, on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    delink_tray = models.BooleanField(default=False, help_text="Is tray delinked")
    delink_tray_qty = models.CharField(max_length=50, null=True, blank=True, help_text="Delinked quantity")

 
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id} - {self.tray_quantity}"

    
#unique_id history model

class UniqueIDHistory(models.Model):
    model_master_creation = models.ForeignKey(ModelMasterCreation, on_delete=models.CASCADE)
    current_case_quantity = models.IntegerField(default=0)  # New field for missing quantity
    is_checked = models.BooleanField(default=False)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_reason = models.TextField(default="No reason provided")  # Default value for modified reason
    datetime = models.DateTimeField(auto_now_add=True)
    current_batch_quantity=models.IntegerField(default=0)
    is_modified = models.BooleanField(default=False)  # New field to indicate if the record is modified

    def __str__(self):
        return f"History for {self.model_master_creation.unique_id} by {self.modified_by.username} on {self.datetime}"
       
class TotalStockModel(models.Model):
    """
    This model is for saving overall stock in Day Planning operation form.
  
    """
    batch_id = models.ForeignKey(ModelMasterCreation, on_delete=models.CASCADE, null=True, blank=True)

    model_stock_no = models.ForeignKey(ModelMaster, on_delete=models.CASCADE, help_text="Model Stock Number")
    version = models.ForeignKey(Version, on_delete=models.CASCADE, help_text="Version")
    total_stock = models.IntegerField(help_text="Total stock quantity")
    polish_finish = models.ForeignKey(PolishFinishType, on_delete=models.SET_NULL, null=True, blank=True, help_text="Polish Finish")
    
    balance_quantity = models.IntegerField(help_text="Balance quantity") #need to check 
    assigned_quantity = models.IntegerField(help_text="Assigned quantity")
    
    plating_color = models.ForeignKey(Plating_Color, on_delete=models.SET_NULL, null=True, blank=True, help_text="Plating Color")
    location = models.ManyToManyField(Location, blank=True, help_text="Multiple Locations")
    lot_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Lot ID")
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    # day planning missing qty in day planning pick table
    day_planning_missing_qty = models.IntegerField(default=0, help_text="Missing quantity in day planning")
    day_planning_assigned_qty = models.IntegerField(help_text="Original assigned quantity", default=0)  # New field
    
    # New fields for process tracking
    last_process_date_time = models.DateTimeField(null=True, blank=True, help_text="Last Process Date/Time")
    last_process_module = models.CharField(max_length=255, null=True, blank=True, help_text="Last Process Module")
    next_process_module = models.CharField(max_length=255, null=True, blank=True, help_text="Next Process Module")

    #IP Module accept and rejection
    total_IP_accpeted_quantity = models.IntegerField(default=0, help_text="Total accepted quantity")
    total_qty_after_rejection_IP = models.IntegerField(default=0, help_text="Total rejected quantity")
    
    #Brass QC Module accept and rejection
    brass_qc_accepted_qty = models.IntegerField(default=0, help_text="Brass QC Accepted Quantity")  # New field
    brass_qc_after_rejection_qty = models.IntegerField(default=0, help_text="Brass QC Rejected Quantity")  # New field
    
    #IQF Module accept and rejection
    iqf_accept_qty_after_accept_ftn = models.IntegerField(default=0, help_text="IQF Accepted Quantity")  # New field
    iqf_accepted_qty = models.IntegerField(default=0, help_text="IQF Accepted Quantity")  # New field
    iqf_after_rejection_qty = models.IntegerField(default=0, help_text="IQF Rejected Quantity")  # New field
    
    #IP Verification and tray_scan
    tray_scan_status = models.BooleanField(default=False, help_text="Tray scan status")
    ip_person_qty_verified = models.BooleanField(default=False, help_text="IP Person Quantity Verified")  # New field
    accepted_Ip_stock = models.BooleanField(default=False, help_text="Accepted IP Stock")  # New fiel
    few_cases_accepted_Ip_stock = models.BooleanField(default=False, help_text="Few Accepted IP Stock")  # New field
    rejected_ip_stock = models.BooleanField(default=False, help_text="Rejected IP Stock")  # New field
    wiping_status = models.BooleanField(default=False, help_text="Wiping Status")  # New field
   
    rejected_tray_scan_status=models.BooleanField(default=False)
    accepted_tray_scan_status=models.BooleanField(default=False)
    
    #Brass QC Module accept and rejection
    brass_qc_accptance=models.BooleanField(default=False)
    brass_qc_few_cases_accptance=models.BooleanField(default=False)
    brass_qc_rejection=models.BooleanField(default=False)
    brass_rejection_tray_scan_status=models.BooleanField(default=False)
    brass_accepted_tray_scan_status=models.BooleanField(default=False)
    
    #IQF Module accept and rejection
    iqf_acceptance=models.BooleanField(default=False)
    iqf_few_cases_acceptance=models.BooleanField(default=False)
    iqf_rejection=models.BooleanField(default=False)
    iqf_rejection_tray_scan_status=models.BooleanField(default=False)
    iqf_accepted_tray_scan_status=models.BooleanField(default=False)
    
    #Module is IQF - Acceptance - Send to Brass QC 
    send_brass_qc=models.BooleanField(default=False, help_text="Send to Brass QC")
    
    # New fields for Jig status
    jig_full_cases = models.BooleanField(default=False, help_text="Indicates if jig is loaded with full cases")
    jig_full_cases_qty=models.IntegerField(default=0, help_text="JIG Full Quantity")
    jig_remining_cases = models.BooleanField(default=False, help_text="Indicates if jig has remaining cases")
    jig_remaining_cases_qty=models.IntegerField(default=0, help_text="JIG Remaining Quantity")
    
    
    # Override the save method to calculate day_planning_assigned_qty
    def save(self, *args, **kwargs):
        self.day_planning_assigned_qty = self.assigned_quantity + self.day_planning_missing_qty
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.model_stock_no.model_no} - {self.version.version_name} - {self.lot_id}"



class DP_TrayIdRescan(models.Model):
    """
    Stores tray ID rescans during the day planning process.
    """
    tray_id = models.CharField(max_length=100, unique=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_count = models.PositiveIntegerField(default=1)  # Count how many times scanned

    class Meta:
        unique_together = ('tray_id', 'lot_id')  # Ensure each tray_id and lot_id combination is unique

    def __str__(self):
        return f"{self.tray_id} - {self.lot_id} (Scanned: {self.scan_count})"

class IP_RejectionGroup(models.Model):
    group_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.group_name

class IP_Rejection_Table(models.Model):
    group = models.ForeignKey(IP_RejectionGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejection_reasons')
    rejection_reason_id = models.CharField(max_length=10, null=True, blank=True, editable=False)
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def save(self, *args, **kwargs):
        if not self.rejection_reason_id:
            last = IP_Rejection_Table.objects.order_by('-rejection_reason_id').first()
            if last and last.rejection_reason_id.startswith('R'):
                last_num = int(last.rejection_reason_id[1:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.rejection_reason_id = f"R{new_num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"
    
class Brass_QC_Rejection_Table(models.Model):
    brass_rejection_reason = models.TextField(help_text="Reason for rejection")
    brass_rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def __str__(self):
        return f"{self.brass_rejection_reason} - {self.brass_rejection_count}"
    
class IQF_Rejection_Table(models.Model):
    iqf_rejection_reason = models.TextField(help_text="Reason for rejection")
    iqf_rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def __str__(self):
        return f"{self.iqf_rejection_reason} - {self.iqf_rejection_count}"
    
#rejection reasons stored tabel , fields ared rejection resoon multiple slection from RejectionTable an dlot_id , user, Total_rejection_qunatity
class IP_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(IP_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"
    
class Brass_QC_Rejection_ReasonStore(models.Model):
    brass_rejection_reason = models.ManyToManyField(Brass_QC_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brass_total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    brass_batch_rejection=models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    
    def __str__(self):
        return f"{self.user} - {self.brass_total_rejection_quantity} - {self.lot_id}"

class IQF_Rejection_ReasonStore(models.Model):
    iqf_rejection_reason = models.ManyToManyField(IQF_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    iqf_total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    iqf_batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.iqf_total_rejection_quantity} - {self.lot_id}"
    
#give rejected trayscans - fields are lot_id , rejected_tray_quantity , rejected_reson(forign key from RejectionTable), user
class IP_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejection_reason = models.ForeignKey(IP_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"

class Brass_QC_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    brass_rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    brass_rejection_reason = models.ForeignKey(Brass_QC_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.brass_rejection_reason} - {self.brass_rejected_tray_quantity} - {self.lot_id}"
    
class IQF_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    iqf_rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    iqf_rejection_reason = models.ForeignKey(IQF_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.iqf_rejection_reason} - {self.iqf_rejected_tray_quantity} - {self.lot_id}"
    
#give accpeted tray scan - fields are lot_id , accepted_tray_quantity , user    
class IP_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"

class Brass_Qc_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    brass_accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.brass_accepted_tray_quantity} - {self.lot_id}"
    
class IQF_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    iqf_accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.iqf_accepted_tray_quantity} - {self.lot_id}"
    
#give accepted tray scan in input screening - fields are lot_id , tray_id , user
class IP_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"
    
class Brass_Qc_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"

class IQF_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"
    

#jig Loading master
class JigLoadingMaster(models.Model):
    model_stock_no = models.ForeignKey(ModelMaster, on_delete=models.CASCADE, help_text="Model Stock Number")
    jig_type=models.CharField(max_length=100, help_text="Jig Type")
    jig_capacity=models.IntegerField(help_text="Jig Capacity")
    forging_info=models.CharField(max_length=100, help_text="Forging Info")
    
    def __str__(self):
        return f"{self.model_stock_no} - {self.jig_type} - {self.jig_capacity}"
    
class BathNumber(models.Model):
    bath_number = models.CharField(max_length=100, unique=True, help_text="Bath Number")
    bath_tub = models.CharField(max_length=100, help_text="Bath Tub",blank=True, null=True)
    
    def __str__(self):
        return self.bath_number


class JigDetails(models.Model):
    jig_qr_id = models.CharField(max_length=100)
    faulty_slots = models.IntegerField(default=0)
    jig_type = models.CharField(max_length=50)  # New field
    jig_capacity = models.IntegerField()        # New field
    bath_number = models.CharField(max_length=50)
    bath_tub = models.CharField(max_length=100, help_text="Bath Tub",blank=True, null=True)
    plating_color = models.CharField(max_length=50)
    empty_slots = models.IntegerField(default=0)
    ep_bath_type = models.CharField(max_length=50)
    total_cases_loaded = models.IntegerField()
        #JIG Loading Module - Remaining cases
    jig_cases_remaining_count=models.IntegerField(default=0,blank=True,null=True)

    forging = models.CharField(max_length=100)
    no_of_model_cases = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    no_of_cycle=models.IntegerField(default=30)
    lot_id = models.CharField(max_length=100)
    new_lot_ids = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    electroplating_only = models.BooleanField(default=False)
    lot_id_quantities = JSONField(blank=True, null=True)


    def __str__(self):
        return f"{self.jig_qr_id} - {self.lot_id} - {self.no_of_cycle}"


from django.db import models

class InspectionAccept(models.Model):
    # Define the fields for the InspectionAccept model
    lot_id = models.CharField(max_length=255,help_text="Unique identifier for the lot.")
    jig_id = models.CharField(max_length=255, help_text="Identifier for the jig used in inspection.")
    sample_count = models.PositiveIntegerField(help_text="Number of samples inspected.")
    position = models.CharField(max_length=255, help_text="Position of the sample during inspection.")
    
    # Optional: You can also add additional fields like timestamps if required
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the record is created.")

    def __str__(self):
        return f"Inspection for Lot {self.lot_id} at {self.position}"
    
class InspectRejectionReasonTable(models.Model):
    rejection_reason = models.TextField(help_text="Reason for rejection")

    def __str__(self):
        return f"{self.rejection_reason}"
    
class InspectionReject(models.Model):
    # Define the fields for the InspectionReject model
    lot_id = models.CharField(max_length=255,help_text="Unique identifier for the lot.")
    jig_id = models.CharField(max_length=255, help_text="Identifier for the jig used in inspection.")
    sample_count = models.PositiveIntegerField(help_text="Number of samples inspected.")
    position = models.CharField(max_length=255, help_text="Position of the sample during inspection.")
    Reason=models.ForeignKey(InspectRejectionReasonTable, on_delete=models.CASCADE, help_text="Reason for rejection")
        
    # Optional: You can also add additional fields like timestamps if required
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the record is created.")

    def __str__(self):
        return f"Inspection for Lot {self.lot_id} at {self.position}"   

  
