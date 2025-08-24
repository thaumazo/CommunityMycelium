from django import forms
from django.forms import inlineformset_factory
from .models import Book, Content, ComprehensionWithin, ComprehensionAbout

CATEGORY_CHOICES = [
    ('Fiction', 'Fiction'),
    ('Nonfiction', 'Nonfiction'),
]

class BookForm(forms.ModelForm):
    level = forms.CharField(max_length=1, label="Level")
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label="Category")
    writing_prompt = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), label="Writing Prompt")

    class Meta:
        model = Book
        fields = ["title", "description", "level", "category", "writing_prompt"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ["page", "text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 2}),
        }

class ComprehensionWithinForm(forms.ModelForm):
    class Meta:
        model = ComprehensionWithin
        fields = ["question"]
        widgets = {
            "question": forms.Textarea(attrs={"rows": 2}),
        }

class ComprehensionAboutForm(forms.ModelForm):
    class Meta:
        model = ComprehensionAbout
        fields = ["question"]
        widgets = {
            "question": forms.Textarea(attrs={"rows": 2}),
        }

ContentFormSet = inlineformset_factory(Book, Content, form=ContentForm, extra=8, can_delete=True)
ComprehensionWithinFormSet = inlineformset_factory(Book, ComprehensionWithin, form=ComprehensionWithinForm, extra=4, can_delete=True)
ComprehensionAboutFormSet = inlineformset_factory(Book, ComprehensionAbout, form=ComprehensionAboutForm, extra=4, can_delete=True)