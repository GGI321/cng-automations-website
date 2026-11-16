
from django import forms

from .models import ContactEnquiry, Project


class ContactEnquiryForm(forms.ModelForm):
    class Meta:
        model = ContactEnquiry
        fields = [
            "name",
            "email",
            "company",
            "service",
            "budget",
            "message",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"maxlength": 120}),
            "email": forms.EmailInput(),
            "company": forms.TextInput(attrs={"maxlength": 150}),
            "service": forms.Select(),
            "budget": forms.TextInput(attrs={"maxlength": 100}),
            "message": forms.Textarea(),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError(
                "Please provide at least 10 characters about your project."
            )
        return message


class ProjectForm(forms.ModelForm):
    """Validated editor for portfolio projects; slugs remain model-managed."""

    class Meta:
        model = Project
        fields = [
            "title", "short_description", "category", "technologies",
            "featured_image", "problem", "solution", "implementation",
            "live_demo_url", "source_code_url", "video_url",
            "is_featured", "is_published",
        ]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "problem": forms.Textarea(attrs={"rows": 5}),
            "solution": forms.Textarea(attrs={"rows": 5}),
            "implementation": forms.Textarea(attrs={"rows": 5}),
            "is_featured": forms.CheckboxInput(),
            "is_published": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-400 focus:ring-emerald-400"
            else:
                field.widget.attrs["class"] = "mt-2 block w-full rounded-xl border border-white/10 bg-[#080B12] px-4 py-3 text-white placeholder-gray-500 focus:border-emerald-400 focus:outline-none"
        self.fields["featured_image"].help_text = "Optional. Upload a JPG, PNG, GIF, or WebP image up to 5 MB."

    def clean_featured_image(self):
        image = self.cleaned_data.get("featured_image")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image files must be 5 MB or smaller.")
        return image
