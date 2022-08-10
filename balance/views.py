from django.shortcuts import render

# Create your views here.
def BalanceEnquiry(request):
    return render(request,"balance.html")