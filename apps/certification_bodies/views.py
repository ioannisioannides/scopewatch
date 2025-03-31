# apps/certification_bodies/views.py

from django.http import HttpResponse

def certbody_list_view(request):
    return HttpResponse("Cert Bodies Placeholder")

def certbody_detail_view(request, cb_id):
    return HttpResponse(f"Detail of Certification Body ID: {cb_id}")
