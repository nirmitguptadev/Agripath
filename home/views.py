from django.shortcuts import HttpResponse,render


def index(request):
    return render(request,'index.html')

def Bihar(request):
    return render(request,'Bihar.html')

def Policies(request):
    return render(request,'Policies.html')

def about(request):
    return render(request,'about.html')

def Uttar(request):
    return render(request,'UttarPradesh.html')

def Har(request):
    return render(request,'Haryana.html')