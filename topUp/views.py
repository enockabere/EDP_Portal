from django.shortcuts import render

# Create your views here.
def LoanTopUp(request):
    return render(request,"topUp.html")

def TopUpDetails(request,pk):
    
    return render(request,"topUpDetails.html")