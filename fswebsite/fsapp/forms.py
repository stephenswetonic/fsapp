from django import forms
from django.forms import ModelForm
from .models import FSJob, FSImage

class FSJobForm(ModelForm):
    class Meta:
        model = FSJob
        fields = ('description',)

class ImageForm(ModelForm):
    image = forms.ImageField(label='image')
    class Meta:
        model = FSImage
        fields = ('image',)