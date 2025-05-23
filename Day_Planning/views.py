from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render

# Create your views here.
class BulkUpload(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Day_Planning/DP_BulkUpload.html'

    def get(self, request, format=None):
        # You can pass additional context data to your template by adding it to the context dict.
        context = {}
        return Response(context)
    
class IndexView(APIView):
    def get(self, request):
        return render(request, 'Day_Planning/DP_PickTable.html')

class DPPickTableView(APIView):
    def get(self, request):
        return render(request, 'Day_Planning/DP_PickTable.html')
    
    
class DPCompletedTableView(APIView):
    def get(self, request):
        return render(request, 'Day_Planning/DP_Completed_Table.html')
