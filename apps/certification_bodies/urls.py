from django.urls import path
from . import views

urlpatterns = [
    path('', views.certbody_list_view, name='certbody_list'),  # List view
    path('<int:cb_id>/', views.certbody_detail_view, name='certbody_detail'),  # Detail view
]