
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("ai_agents", "AI Agents"),
        ("workflow_automation", "Workflow Automation"),
        ("crm", "CRM & Lead Management"),
        ("chatbots", "Chatbots & Customer Support"),
        ("web_development", "Web Development"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    short_description = models.CharField(max_length=300)
    problem = models.TextField()
    solution = models.TextField()
    implementation = models.TextField(blank=True)

    featured_image = models.ImageField(
        upload_to="projects/",
        blank=True,
    )

    # Comma-separated technology names, e.g. n8n, Python, PostgreSQL
    technologies = models.CharField(max_length=300)

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other",
    )

    live_demo_url = models.URLField(blank=True)
    source_code_url = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-is_featured", "-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "project"
            slug = base_slug
            counter = 2

            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    @property
    def technology_list(self):
        return [
            technology.strip()
            for technology in self.technologies.split(",")
            if technology.strip()
        ]

from django.db import models


class ContactEnquiry(models.Model):
    SERVICE_CHOICES = [
        ("ai_agents", "AI Agents"),
        ("workflow_automation", "Workflow Automation"),
        ("crm_automation", "CRM Automation"),
        ("chatbots", "AI Chatbots"),
        ("web_development", "Web Development"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("in_progress", "In Progress"),
        ("converted", "Converted"),
        ("closed", "Closed"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    service = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
    )
    budget = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Enquiry"
        verbose_name_plural = "Contact Enquiries"

    def __str__(self):
        return f"{self.name} — {self.email}"
