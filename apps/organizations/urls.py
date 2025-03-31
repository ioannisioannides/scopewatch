from django.urls import path
from . import views

urlpatterns = [
    path('', views.organization_list_view, name='organization_list'),  # List view
    path('<int:org_id>/', views.organization_detail_view, name='organization_detail'),  # Detail view
]