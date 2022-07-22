#from turtle import update
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from numpy import delete
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import FSJob, FSImage
from .serializers import FSJobSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from .forms import ArticleForm, FSJobForm, ImageForm
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.forms import modelformset_factory
import datetime
import time
from celery import shared_task
from .tasks import add


def index(request):
  return render(request, 'fsapp/index.html')

def fsjob_form(request):
  print('in view function')
  if request.method == 'POST':
    if 'first form' in request.POST:
      print('this was from the first form')
      data = request.POST
      images = request.FILES.getlist('images')
      #job = FSJob.objects.create(description=data['description'])
      job = FSJob(description = data['description'])
      job.save()

      for image in images:
        img = FSImage(image = image, FSJob = job)
        img.save()
      return redirect('/fsmain/' + str(job.id) + '/', job.id)

    if 'second form' in request.POST:
      print('this was from the second form')
  return render(request, 'fsapp/fsjob_form.html')

def fsmain(request, id):
  job = FSJob.objects.get(id = id)
  images = job.fsimage_set.all()
  return render(request, 'fsapp/fsmain.html', {'images' : images})

def streamA(request):
  task1 = add.delay(1,2)
  task2 = add.delay(3,4)
  task3 = add.delay(5,6)
  return render(request, 'fsapp/ssetest.html', {'task_id' : [task1.id, task2.id, task3.id]})

def streamB(request):

  if request.method == 'POST':
    # getting list of task ids and separating by commas
    unfinished_tasks = []
    post_list = request.POST.get('task_id')
    post_list_cleaned = []

    post_list = post_list.split(',')

    #print(post_list)

    # remove brackets and escaped characters
    for i in range(len(post_list)):
      item = post_list[i]
      item = item.replace('&#x27;', '')
      item = item.replace('[', '')
      item = item.replace(']', '')
      item = item.strip()
      post_list_cleaned.append(item)


    #print(post_list_cleaned)
    # if task not done, add it to the unfinished list
    for i in range(len(post_list_cleaned)):
      task = add.AsyncResult(post_list_cleaned[i])
      print(task)
      if not task.ready():
        #print('added task')
        unfinished_tasks.append(task)

    print(unfinished_tasks)
    # if tasks are left, pop one if ready
    if len(unfinished_tasks) > 0:
      if unfinished_tasks[0].ready():
        unfinished_tasks.pop(0)
    # Return ok when all are done
    else:
      return JsonResponse({'finished_id': len(unfinished_tasks)}, safe=False, status=200) #200


    return JsonResponse({'finished_ids': len(unfinished_tasks)}, safe=False, status=404) #404

  return render(request, 'fsapp/ssetestb.html')
  
def celerytest(request):
  task1 = add.delay(1,2)
  task2 = add.delay(3,4)
  task3 = add.delay(5,6)

  id1 = task1.id
  id2 = task2.id
  id3 = task3.id

  results = [add.AsyncResult(id1), add.AsyncResult(id2), add.AsyncResult(id3)]

  for i in range(25):
    time.sleep(5)
    for result in results:
      print(result)
      print(result.ready())

  return render(request, 'fsapp/celerytest.html')


def add_article(request):
  submitted = False

  if request.method == 'POST':
    form = ArticleForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect('/add_article?submitted=True')
  else:
    form = ArticleForm
    if submitted in request.GET:
      submitted = True
  return render(request, 'fsapp/add_article.html', {"form": form, "submitted": submitted})

class FSJobAPIView(APIView):

  def get(self, request):
    articles = FSJob.objects.all()
    serializer = FSJobSerializer(articles, many=True)

    return Response(serializer.data)
  
  def post(self, request):
    serializer = FSJobSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status = status.HTTP_201_CREATED)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

# class ArticleDetails(APIView):

#   def get_object(self, id):
#     try:
#       return Article.objects.get(id = id)
#     except Article.DoesNotExist:
#       return HttpResponse(status=status.HTTP_404_NOT_FOUND)

#   def get(self, request, id):
#     article = self.get_object(id)
#     serializer = ArticleSerializer(article)
#     return Response(serializer.data)

#   def put(self, request, id):
#     article = self.get_object(id)
#     serializer = ArticleSerializer(article, data = request.data)

#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#     return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

#   def delete(self, request, id):
#     article = self.get_object(id)
#     article.delete()
#     return HttpResponse(status = status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'POST'])
# def article_list(request):
#   if request.method == 'GET':
#     articles = Article.objects.all()
#     serializer = ArticleSerializer(articles, many=True)
#     return Response(serializer.data)

#   elif request.method == 'POST':
#     serializer = ArticleSerializer(data=request.data)

#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data, status = status.HTTP_201_CREATED)
#     return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def article_detail(request, pk):
#   try:
#     article = Article.objects.get(pk=pk)
#   except Article.DoesNotExist:
#     return HttpResponse(status=status.HTTP_404_NOT_FOUND)

#   if request.method == 'GET':
#     serializer = ArticleSerializer(article)
#     return Response(serializer.data)

#   elif request.method == 'PUT':
#     serializer = ArticleSerializer(article, data = request.data)

#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#     return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

#   elif request.method == 'DELETE':
#     article.delete()
#     return HttpResponse(status = status.HTTP_204_NO_CONTENT)

# class GenericAPIView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin, 
#                      mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):

#   serializer_class = ArticleSerializer
#   queryset = Article.objects.all()
#   lookup_field = 'id'
#   authentication_classes = [SessionAuthentication, BasicAuthentication]
#   permission_classes = [IsAuthenticated]
#   #renderer_classes = [TemplateHTMLRenderer]
#   #template_name = 'fsapp/testform.html'

#   def get(self, request, id = None):
#     if id:
#       return self.retrieve(request)
#     else:
#       return self.list(request)

#   def post(self, request, id = None):
#     return self.create(request)

#   def put(self, request, id = None):
#     return self.update(request, id)

#   def delete(self, request, id = None):
#     return self.destroy(request, id)

