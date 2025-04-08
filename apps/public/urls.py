"""
URL patterns for the Public app.

This module defines URL patterns for public-facing features like certificate verification.
"""

from django.urls import path

from . import views

app_name = 'public'

urlpatterns = [
    path('', views.CertificateSearchView.as_view(), name='certificate_search'),
    path('certificate/<int:pk>/', views.CertificateDetailView.as_view(), name='certificate_detail'),
    path('api/verify/', views.verify_certificate_api, name='verify_api'),
]
