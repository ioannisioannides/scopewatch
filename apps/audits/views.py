# apps/audits/views.py

from django.shortcuts import render
from django.http import HttpResponse
from .models import Audit

def audit_list_view(request):
    audits = Audit.objects.all()
    return render(request, 'audits/audit_list.html', {'audits': audits})

def audit_detail_view(request, audit_id):
    audit = Audit.objects.get(id=audit_id)
    return render(request, 'audits/audit_detail.html', {'audit': audit})
