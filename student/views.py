from django.shortcuts import render

def home(request):
    return render(request,"student/home.html")
# Create your views here.
