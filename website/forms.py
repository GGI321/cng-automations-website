
from django import forms

from .models import ContactEnquiry


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
