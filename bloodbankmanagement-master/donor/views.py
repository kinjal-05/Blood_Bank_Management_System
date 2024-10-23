from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        donor = models.Donor.objects.get(user_id=request.user.id)
        context = {
            'requestpending': bmodels.BloodRequest.objects.filter(request_by_donor=donor, status='Pending').count(),
            'requestapproved': bmodels.BloodRequest.objects.filter(request_by_donor=donor, status='Approved').count(),
            'requestmade': bmodels.BloodRequest.objects.filter(request_by_donor=donor).count(),
            'requestrejected': bmodels.BloodRequest.objects.filter(request_by_donor=donor, status='Rejected').count(),
        }
        response = render(request, 'donor/donor_dashboard.html', context)
        # Set cache-control headers to prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
        response['Pragma'] = 'no-cache'  # HTTP 1.0
        response['Expires'] = '0'  # Proxies
        return response
    else:
        # Redirect to the login page if the user is not authenticated
        return redirect('donorlogin')  # Change 'donorlogin' to the appropriate URL name



def donate_blood_view(request):
    donation_form=forms.DonationForm()
    if request.method=='POST':
        donation_form=forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate=donation_form.save(commit=False)
            blood_donate.bloodgroup=donation_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_donate.donor=donor
            blood_donate.save()
            return HttpResponseRedirect('donation-history')  
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form})

def donation_history_view(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        donor = models.Donor.objects.get(user_id=request.user.id)
        donations = models.BloodDonate.objects.filter(donor=donor)
        context = {'donations': donations}
        response = render(request, 'donor/donation_history.html', context)
        # Set cache-control headers to prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
        response['Pragma'] = 'no-cache'  # HTTP 1.0
        response['Expires'] = '0'  # Proxies
        return response
    else:
        # Redirect to the login page if the user is not authenticated
        return redirect('donorlogin')  # Change 'donorlogin' to the appropriate URL name


def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})


def request_history_view(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        donor = models.Donor.objects.get(user_id=request.user.id)
        blood_requests = bmodels.BloodRequest.objects.filter(request_by_donor=donor)
        context = {'blood_requests': blood_requests}
        response = render(request, 'donor/request_history.html', context)
        # Set cache-control headers to prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
        response['Pragma'] = 'no-cache'  # HTTP 1.0
        response['Expires'] = '0'  # Proxies
        return response
    else:
        # Redirect to the login page if the user is not authenticated
        return redirect('donorlogin')  # Change 'donorlogin' to the appropriate URL name
