from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone
from PIL import Image

from .models import Project


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("staff", password="safe-test-pass", is_staff=True)
        cls.member = User.objects.create_user("member", password="safe-test-pass")

    def valid_project_data(self, **overrides):
        data = {
            "title": "Lead routing automation",
            "short_description": "Routes incoming leads to the right team.",
            "category": "workflow_automation",
            "technologies": "n8n, Python",
            "problem": "Leads were assigned manually.",
            "solution": "New leads are routed automatically.",
            "implementation": "Connected form, CRM and notifications.",
            "live_demo_url": "https://example.com/demo",
            "source_code_url": "https://github.com/example/project",
            "video_url": "https://youtube.com/watch?v=example",
            "is_featured": "on",
            "is_published": "on",
        }
        data.update(overrides)
        return data

    @staticmethod
    def png_upload(name="preview.png"):
        buffer = BytesIO()
        Image.new("RGB", (2, 2), "green").save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    def test_staff_only_access(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/admin/login/?next="))
        self.assertIn("next=/dashboard/", response["Location"])

        project = Project.objects.create(
            title="Access test", short_description="Description", problem="Problem",
            solution="Solution", technologies="Django",
        )
        protected_urls = [
            reverse("dashboard"),
            reverse("dashboard_projects"),
            reverse("dashboard_project_add"),
            reverse("dashboard_project_edit", args=[project.pk]),
            reverse("dashboard_project_delete", args=[project.pk]),
        ]
        self.client.force_login(self.member)
        for url in protected_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/dashboard/overview.html")
        self.assertTemplateUsed(response, "website/dashboard/base.html")
        self.assertTemplateUsed(response, "website/base.html")

    def test_dashboard_navigation_targets_resolve(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard"))
        for url_name in ("dashboard", "dashboard_projects", "dashboard_project_add"):
            self.assertContains(response, f'href="{reverse(url_name)}"')
        response = self.client.get(reverse("dashboard_projects"))
        self.assertContains(response, f'href="{reverse("projects")}"')

    def test_project_urls_resolve(self):
        self.assertEqual(resolve("/dashboard/").url_name, "dashboard")
        self.assertEqual(resolve("/dashboard/projects/").url_name, "dashboard_projects")
        self.assertEqual(resolve("/dashboard/projects/add/").url_name, "dashboard_project_add")
        self.assertEqual(resolve("/dashboard/projects/4/edit/").url_name, "dashboard_project_edit")
        self.assertEqual(resolve("/dashboard/projects/4/delete/").url_name, "dashboard_project_delete")

    def test_creation_upload_slug_and_public_listing(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("dashboard_project_add"),
            {**self.valid_project_data(), "featured_image": self.png_upload()},
        )
        self.assertRedirects(response, reverse("dashboard_projects"))
        project = Project.objects.get()
        self.assertEqual(project.slug, "lead-routing-automation")
        self.assertTrue(project.featured_image.name.startswith("projects/"))
        self.assertIsNotNone(project.published_at)
        self.assertContains(self.client.get(reverse("projects")), project.title)

        saved_image_name = project.featured_image.name
        response = self.client.post(
            reverse("dashboard_project_edit", args=[project.pk]),
            self.valid_project_data(title=project.title, short_description="Updated description"),
        )
        self.assertRedirects(response, reverse("dashboard_projects"))
        project.refresh_from_db()
        self.assertEqual(project.featured_image.name, saved_image_name)

    def test_publish_date_is_preserved_cleared_and_reset(self):
        project = Project.objects.create(
            title="Timestamp test", short_description="Description", problem="Problem",
            solution="Solution", technologies="Django", is_published=True,
            published_at=timezone.now() - timedelta(days=3),
        )
        original_date = project.published_at
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("dashboard_project_edit", args=[project.pk]),
            self.valid_project_data(title=project.title),
        )
        self.assertRedirects(response, reverse("dashboard_projects"))
        project.refresh_from_db()
        self.assertEqual(project.published_at, original_date)

        response = self.client.post(
            reverse("dashboard_project_edit", args=[project.pk]),
            self.valid_project_data(title=project.title, is_published=""),
        )
        self.assertRedirects(response, reverse("dashboard_projects"))
        project.refresh_from_db()
        self.assertFalse(project.is_published)
        self.assertIsNone(project.published_at)

        response = self.client.post(
            reverse("dashboard_project_edit", args=[project.pk]),
            self.valid_project_data(title=project.title),
        )
        self.assertRedirects(response, reverse("dashboard_projects"))
        project.refresh_from_db()
        self.assertTrue(project.is_published)
        self.assertGreater(project.published_at, original_date)

    def test_image_validation_and_delete_requires_post(self):
        self.client.force_login(self.staff)
        project = Project.objects.create(
            title="Delete test", short_description="Description", problem="Problem",
            solution="Solution", technologies="Django",
        )
        delete_url = reverse("dashboard_project_delete", args=[project.pk])
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())
        self.assertEqual(self.client.post(delete_url).status_code, 302)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

        form = self.client.post(
            reverse("dashboard_project_add"),
            {**self.valid_project_data(title="Bad image"), "featured_image": SimpleUploadedFile("bad.png", b"not an image", content_type="image/png")},
        )
        self.assertEqual(form.status_code, 200)
        self.assertFalse(Project.objects.filter(title="Bad image").exists())
        self.assertContains(form, "Upload a valid image")
