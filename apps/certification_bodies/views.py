# apps/certification_bodies/views.py

"""
Views for the Certification Bodies app.

This module contains views for listing certification bodies, displaying their details, and managing certification issuance based on audit results.
"""

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from apps.audits.models import Audit, AuditResult
from apps.organizations.models import Certification
from .models import CertBody, CertBodyUser
from .forms import CertificationIssueForm, AuditDecisionForm

# Suppress pylint no-member warnings for CertBody
# pylint: disable=no-member


def certbody_list_view(request):
    """
    View for listing all certification bodies.
    """
    cert_bodies = CertBody.objects.all()
    return render(
        request, "certification_bodies/certbody_list.html", {"cert_bodies": cert_bodies}
    )


def certbody_detail_view(request, cb_id):
    """
    View for displaying the details of a specific certification body.
    """
    cert_body = get_object_or_404(CertBody, id=cb_id)
    return render(
        request, "certification_bodies/certbody_detail.html", {"cert_body": cert_body}
    )


@method_decorator(login_required, name='dispatch')
class AuditPendingDecisionListView(ListView):
    """
    View for listing audits that need certification decisions.
    """
    model = Audit
    template_name = 'certification_bodies/pending_decision_list.html'
    context_object_name = 'audits'
    
    def get_queryset(self):
        # Get the certification body user
        try:
            cert_body_user = self.request.user.cert_body_roles.filter(is_active=True).first()
            if not cert_body_user:
                return Audit.objects.none()
                
            # Get audits from this cert body that are completed but don't have results
            return Audit.objects.filter(
                certbody=cert_body_user.cert_body,
                status='completed'
            ).exclude(
                pk__in=AuditResult.objects.values_list('audit', flat=True)
            )
        except:
            return Audit.objects.none()


@login_required
def audit_decision_view(request, audit_id):
    """
    View for making certification decisions for an audit.
    """
    audit = get_object_or_404(Audit, pk=audit_id)
    
    # Check if the user is authorized (belongs to the cert body)
    try:
        cert_body_user = request.user.cert_body_roles.filter(
            cert_body=audit.certbody, 
            is_active=True
        ).first()
        if not cert_body_user:
            messages.error(request, "You are not authorized to make decisions for this audit.")
            return redirect('certification_bodies:dashboard')
    except:
        messages.error(request, "You are not authorized to make decisions for this audit.")
        return redirect('certification_bodies:dashboard')
    
    # Handle form submission
    if request.method == 'POST':
        form = AuditDecisionForm(request.POST)
        if form.is_valid():
            audit_result = form.save(commit=False)
            audit_result.audit = audit
            audit_result.decided_by = cert_body_user
            audit_result.save()
            
            # Update the audit status
            if audit_result.decision in ['approve', 'conditional']:
                audit.status = 'closed'
            elif audit_result.decision == 'followup':
                audit.status = 'in_progress'
            audit.save()
            
            messages.success(request, f"Decision recorded for {audit}")
            
            # If approved, redirect to certificate issuance
            if audit_result.can_issue_certificate():
                return redirect('certification_bodies:issue_certificate', audit_id=audit.pk)
            return redirect('certification_bodies:pending_decisions')
    else:
        form = AuditDecisionForm()
    
    return render(request, 'certification_bodies/audit_decision.html', {
        'audit': audit,
        'form': form,
        'nonconformances': audit.nonconformances.all(),
    })


@login_required
def issue_certificate_view(request, audit_id):
    """
    View for issuing a certificate based on a successful audit.
    """
    audit = get_object_or_404(Audit, pk=audit_id)
    
    # Check if the audit has a result that allows certificate issuance
    try:
        audit_result = audit.result
        if not audit_result.can_issue_certificate():
            messages.error(request, "This audit result does not allow certificate issuance.")
            return redirect('certification_bodies:pending_decisions')
    except AuditResult.DoesNotExist:
        messages.error(request, "This audit doesn't have a decision yet.")
        return redirect('certification_bodies:pending_decisions')
    
    # Check authorization
    try:
        cert_body_user = request.user.cert_body_roles.filter(
            cert_body=audit.certbody, 
            is_active=True
        ).first()
        if not cert_body_user:
            messages.error(request, "You are not authorized to issue certificates for this audit.")
            return redirect('certification_bodies:dashboard')
    except:
        messages.error(request, "You are not authorized to issue certificates for this audit.")
        return redirect('certification_bodies:dashboard')
    
    # Check if certificate already exists
    try:
        if hasattr(audit, 'resulting_certification'):
            messages.warning(request, "A certificate has already been issued for this audit.")
            return redirect('organizations:certification_detail', pk=audit.resulting_certification.pk)
    except Certification.DoesNotExist:
        pass
    
    # Handle form submission
    if request.method == 'POST':
        form = CertificationIssueForm(request.POST)
        if form.is_valid():
            # Generate default expiry date (3 years from now)
            expiry_date = form.cleaned_data.get('expiry_date') or (timezone.now().date() + timedelta(days=365*3))
            
            # Issue the certificate
            try:
                certification = audit_result.issue_certificate(
                    certificate_number=form.cleaned_data['certificate_number'],
                    scope=form.cleaned_data['scope'],
                    expiry_date=expiry_date
                )
                messages.success(request, f"Certificate {certification.certificate_number} issued successfully.")
                return redirect('organizations:certification_detail', pk=certification.pk)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        # Pre-populate with default values
        initial = {
            'scope': f"Scope of certification for {audit.organization.name} - {audit.standard}",
            'certificate_number': f"{audit.certbody.accreditation_id}-{audit.organization.pk}-{timezone.now().strftime('%Y%m')}"
        }
        form = CertificationIssueForm(initial=initial)
    
    return render(request, 'certification_bodies/issue_certificate.html', {
        'audit': audit,
        'form': form,
        'audit_result': audit.result,
    })
