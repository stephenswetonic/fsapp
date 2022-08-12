# Project urls
from django.urls import path
from . import views

urlpatterns = [
  path('fsjob_form/', views.fsjob_form),
  path('fsmain/<int:id>/', views.fsmain),
  path('fsmain_loading/<int:id>/', views.fsmain_loading),
  path('fsmain_loaded/<int:id>/', views.fsmain_loaded),
]