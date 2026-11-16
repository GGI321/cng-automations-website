

from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("projects/", views.projects, name="projects"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/projects/", views.dashboard_projects, name="dashboard_projects"),
    path("dashboard/projects/add/", views.dashboard_project_add, name="dashboard_project_add"),
    path("dashboard/projects/<int:pk>/edit/", views.dashboard_project_edit, name="dashboard_project_edit"),
    path("dashboard/projects/<int:pk>/delete/", views.dashboard_project_delete, name="dashboard_project_delete"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
]

