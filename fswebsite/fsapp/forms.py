from django import forms
from django.forms import ModelForm
from .models import Article, FSJob, FSImage

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

class FSJobForm(ModelForm):
    class Meta:
        model = FSJob
        fields = ('description',)

class ImageForm(ModelForm):
    image = forms.ImageField(label='image')
    class Meta:
        model = FSImage
        fields = ('image',)