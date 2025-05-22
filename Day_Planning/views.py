from django.shortcuts import render

def index(request):
    # You can change the template below to your actual home page if needed
    return render(request, 'Day_Planning/DP_PickTable.html')

def dp_pick_table(request):
    return render(request, 'Day_Planning/DP_PickTable.html')