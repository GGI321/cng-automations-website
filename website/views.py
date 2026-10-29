
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactEnquiryForm
from .models import Project

logger = logging.getLogger(__name__)


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
