from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_featured",
        "is_published",
        "published_at",
        "updated_at",
    )

    list_filter = (
        "category",
        "is_featured",
        "is_published",
    )

    search_fields = (
        "title",
        "short_description",
        "problem",
        "technologies",
    )

    prepopulated_fields = {"slug": ("title",)}

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Project Information", {
            "fields": (
                "title",
                "slug",
                "short_description",
                "category",
                "technologies",
                "featured_image",
            )
        }),
        ("Case Study", {
            "fields": (
                "problem",
                "solution",
                "implementation",
            )
        }),
        ("Links", {
            "fields": (
                "live_demo_url",
                "source_code_url",
            )
        }),
        ("Publishing", {
            "fields": (
                "is_featured",
                "is_published",
                "published_at",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

from django.contrib import admin
from .models import ContactEnquiry


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "company",
        "service",
        "status",
        "created_at",
    )
    list_filter = ("status", "service", "created_at")
    search_fields = ("name", "email", "company", "message")
    list_editable = ("status",)
    readonly_fields = ("created_at",)
