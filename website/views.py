
import logging
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ContactEnquiryForm, ProjectForm
from .models import ContactEnquiry, Project

logger = logging.getLogger(__name__)


def staff_required(view_func):
    """Require authentication and staff status for every management view."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), "/admin/login/")
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped


@staff_required
def dashboard(request):
    recent_projects = Project.objects.order_by("-created_at")[:5]
    return render(request, "website/dashboard/overview.html", {
        "total_projects": Project.objects.count(),
        "published_projects": Project.objects.filter(is_published=True).count(),
        "draft_projects": Project.objects.filter(is_published=False).count(),
        "total_enquiries": ContactEnquiry.objects.count(),
        "recent_projects": recent_projects,
    })


@staff_required
def dashboard_projects(request):
    return render(request, "website/dashboard/projects.html", {
        "projects": Project.objects.all(),
    })


@staff_required
def dashboard_project_add(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        if project.is_published and not project.published_at:
            project.published_at = timezone.now()
        else:
            project.published_at = None
        project.save()
        messages.success(request, "Project created successfully.")
        return redirect("dashboard_projects")
    return render(request, "website/dashboard/project_form.html", {
        "form": form, "page_title": "Add project", "submit_label": "Create project",
    })


@staff_required
def dashboard_project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    was_published = project.is_published
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        if project.is_published:
            if not was_published or not project.published_at:
                project.published_at = timezone.now()
        else:
            project.published_at = None
        project.save()
        messages.success(request, "Project updated successfully.")
        return redirect("dashboard_projects")
    return render(request, "website/dashboard/project_form.html", {
        "form": form, "project": project, "page_title": "Edit project",
        "submit_label": "Save changes",
    })


@staff_required
def dashboard_project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted.")
        return redirect("dashboard_projects")
    return render(request, "website/dashboard/project_confirm_delete.html", {
        "project": project,
    })


def home(request):
    return render(request, "website/home.html")


def about(request):
    return render(request, "website/about.html")


def services(request):
    return render(request, "website/services.html")


def projects(request):
    published_projects = Project.objects.filter(is_published=True)
    return render(
        request,
        "website/projects.html",
        {"projects": published_projects},
    )


def project_detail(request, slug):
    project = get_object_or_404(
        Project,
        slug=slug,
        is_published=True,
    )
    return render(
        request,
        "website/project_detail.html",
        {"project": project},
    )


def contact(request):
    if request.method == "POST":
        form = ContactEnquiryForm(request.POST)

        if form.is_valid():
            enquiry = form.save()

            subject = (
                f"New website enquiry: {enquiry.get_service_display()}"
            )
            body = (
                f"New project enquiry received.\n\n"
                f"Name: {enquiry.name}\n"
                f"Email: {enquiry.email}\n"
                f"Company: {enquiry.company or 'Not provided'}\n"
                f"Service: {enquiry.get_service_display()}\n"
                f"Budget: {enquiry.budget or 'Not provided'}\n\n"
                f"Message:\n{enquiry.message}\n\n"
                f"Received: {enquiry.created_at:%Y-%m-%d %H:%M}\n"
            )

            try:
                if settings.CONTACT_NOTIFICATION_EMAIL:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[
                            settings.CONTACT_NOTIFICATION_EMAIL
                        ],
                        fail_silently=False,
                    )
                else:
                    logger.warning(
                        "Contact notification email is not configured."
                    )
            except Exception:
                # Keep the enquiry saved even if email delivery fails.
                logger.exception(
                    "Could not send contact enquiry notification."
                )

            messages.success(
                request,
                "Thank you! Your enquiry has been received. "
                "We'll be in touch soon.",
            )
            return redirect("contact")

    else:
        form = ContactEnquiryForm()

    return render(
        request,
        "website/contact.html",
        {"form": form},
    )
