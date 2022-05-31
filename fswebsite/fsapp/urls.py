# Project urls
from django.urls import path
from . import views
from .views import FSJobAPIView, add_article, fsjob_form, fsmain

urlpatterns = [
  path('', views.index, name='index'),
  #path('article/', article_list),

  path('fsjob/', FSJobAPIView.as_view()),
  #path('generic/article/', GenericAPIView.as_view()),
  #path('generic/article/<int:id>/', GenericAPIView.as_view()),
  #path('detail/<int:pk>/', article_detail)
  #path('detail/<int:id>/', ArticleDetails.as_view()),
  path('add_article/', views.add_article, name = 'add_article'),
  path('fsjob_form/', views.fsjob_form),
  path('fsmain/<int:id>/', fsmain),
  #path('fsmain/', views.fsmain),
]