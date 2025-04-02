# apps/public/views.py

from django.http import HttpResponse

def public_home_view(request):
    """
    Example view for a public homepage or search form.
    """
    return HttpResponse("Welcome to the Public Portal")

def certificate_search_view(request):
    """
    Example placeholder for a certificate search page.
    """
    return HttpResponse("Certificate Search Placeholder")

def home_view(request):
    """
    View for the root URL (homepage).

    Returns:
        HttpResponse: A simple welcome message.
    """
    return HttpResponse("<h1>Welcome to Scopewatch!</h1><p>This is the homepage.</p>")
