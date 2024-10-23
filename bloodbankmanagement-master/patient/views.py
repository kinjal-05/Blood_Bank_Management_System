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
from django.contrib.auth import logout

def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict)


from django.utils.cache import add_never_cache_headers

def patient_dashboard_view(request):
    if request.user.is_authenticated:
        patient = models.Patient.objects.get(user_id=request.user.id)
        data = {
            'requestpending': bmodels.BloodRequest.objects.filter(request_by_patient=patient, status='Pending').count(),
            'requestapproved': bmodels.BloodRequest.objects.filter(request_by_patient=patient, status='Approved').count(),
            'requestmade': bmodels.BloodRequest.objects.filter(request_by_patient=patient).count(),
            'requestrejected': bmodels.BloodRequest.objects.filter(request_by_patient=patient, status='Rejected').count(),
        }
        response = render(request, 'patient/patient_dashboard.html', context=data)
        add_never_cache_headers(response)  # Add cache-control headers
        return response
    else:
        logout(request)  # Logout the user if they are not authenticated
        return redirect('patientlogin')  # Redirect to the login page



def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()
            return HttpResponseRedirect('my-request')  
    return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    if request.user.is_authenticated:
        patient= models.Patient.objects.get(user_id=request.user.id)
        blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
        response = render(request,'patient/my_request.html',{'blood_request':blood_request})
        add_never_cache_headers(response)  # Add cache-control headers
        return response
    else:
        logout(request)  # Logout the user if they are not authenticated
        return redirect('patientlogin')  # Redirect to the login page
        # return render(request,'patient/my_request.html',{'blood_request':blood_request})
