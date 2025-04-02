# apps/consultants/admin.py

from django.contrib import admin

from .models import ConsultancyFirm, Consultant


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Consultant model.
    """
    list_display = ('id', 'user', 'specialty', 'is_active')
    search_fields = ('user__username', 'specialty')

@admin.register(ConsultancyFirm)
class ConsultancyFirmAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ConsultancyFirm model.
    """
    list_display = ('id', 'name', 'address', 'is_active')
    search_fields = ('name',)
