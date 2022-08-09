import os
import cv2
#import django
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from numpy import delete
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from .models import FSJob, FSImage, FSFilteredImage
from .serializers import FSJobSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from .forms import ArticleForm, FSJobForm, ImageForm
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory
import datetime
import time
from celery import shared_task
from .tasks import add
from .fsprocessor import FSProcessor, align_images, focus_stack
from django.core.files import File
from django.conf import settings
from pathlib import Path
import json
from PIL import Image

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

  cv2_imgs = []
  filter_img_paths = []
  filter_img_path_short = []
  aligned_img_paths = []
  celery_tasks = []
  celery_task_ids = []

  taskid_img_dict = {}

  new_dir = str(settings.MEDIA_ROOT) + '/job' + str(id)
  if not os.path.exists(new_dir):
    os.mkdir(new_dir)

  # Create a list of cv2 images to be aligned
  for i in range(len(images)):
    path = str(settings.MEDIA_ROOT) + '/' + images[i].image.name
    print(path)
    cv2_imgs.append(cv2.imread(str(path)))
  
  
  # Create x test files for each filterimage
  for i in range(len(images)):
    path = new_dir + ('/filterimage' + str(i) + '.png')
    img = File(open(path, 'w'))
    filter_img_paths.append(path)
    filter_img_path_short.append(('/images/job' + str(id) + '/filterimage' + str(i) + '.png'))

  # Create paths for each aligned image
  for i in range(len(images)):
    path = new_dir + ('/alignedimage' + str(i) + '.png')
    img = File(open(path, 'w'))
    aligned_img_paths.append(path)

  # Align
  aligned_imgs = align_images(cv2_imgs)

  # imwrite to aligned img paths
  for i in range(len(aligned_img_paths)):
    cv2.imwrite(aligned_img_paths[i], aligned_imgs[i])

  # Start tasks
  for i in range(len(images)):
    task = focus_stack.delay(aligned_img_paths[i], str(filter_img_paths[i]))
    taskid_img_dict.update({task.id : filter_img_path_short[i]})
    celery_tasks.append(task)
    celery_task_ids.append(task.id)

  # Get tasks ids
  # Give each filter image its task id
  # Tell page how many placeholders to create
  # Give each placeholder the task id

  # When a task finishes, swap the placeholder for the image
  # and update the filter image model



  # filterimg = FSFilteredImage(celery_task_id = '0', FSJob = job)
  # filterimg.save()
  # print(taskid_img_dict)




  return render(request, 'fsapp/fsmain.html', {'images' : images, 'task_ids' : celery_task_ids, 'job_id':id, 'taskid_img_dict': json.dumps(taskid_img_dict) })

# This function gets pinged until all images have loaded (all celery tasks done)
def fsmain_loading(request, id):
  job = FSJob.objects.get(id = id)
  images = job.fsimage_set.all()

  if request.method == 'POST':
    unfinished_tasks = []
    finished_tasks = []
    post_list = request.POST.get('task_ids')
    post_list_cleaned = []

    post_list = post_list.split(',')

    # remove brackets and escaped characters
    for i in range(len(post_list)):
      item = post_list[i]
      item = item.replace('&#x27;', '')
      item = item.replace('[', '')
      item = item.replace(']', '')
      item = item.strip()
      post_list_cleaned.append(item)

    #print(post_list)
    #print(post_list_cleaned)
    # if task not done, add it to the unfinished list
    for i in range(len(post_list_cleaned)):
      task = add.AsyncResult(post_list_cleaned[i])
      #print(task)
      if not task.ready():
        #print('added task')
        unfinished_tasks.append(task)
      else:
        finished_tasks.append(task.id)

    print(finished_tasks)
    # if tasks are left, pop one if ready
    if len(unfinished_tasks) > 0:
      if unfinished_tasks[0].ready():
        #finished_tasks.append(unfinished_tasks[0].id)
        unfinished_tasks.pop(0)
    # Return ok when all are done
    else:
      return JsonResponse({'finished_tasks': finished_tasks}, safe=False, status=200) #200


    return JsonResponse({'finished_tasks': finished_tasks}, safe=False, status=302) # Still processing


  return render(request, 'fsapp/fsmain_loading.html', {'jobid' : id})


def fsmain_loaded(request, id):
  job = FSJob.objects.get(id = id)
  images = job.fsimage_set.all()
  filtered_images = []
  filtered_images_cv2 = []

  result_path = 'static/images/job' + str(id) + '/result' + '.png'
  result_path_template = '/images/job' + str(id) + '/result' + '.png'

  background_fill_path = str(settings.MEDIA_ROOT) + '/' + images[0].image.name


  for i in range(len(images)):
    filtered_images.append('/images/job' + str(id) + '/filterimage' + str(i) + '.png')
    filtered_images_cv2.append('static/images/job' + str(id) + '/filterimage' + str(i) + '.png')

  background = Image.open(background_fill_path)
  background.paste(Image.open(filtered_images_cv2[0]), mask=Image.open(filtered_images_cv2[0]))

  for i in range(len(filtered_images_cv2) - 1):
    background.paste(Image.open(filtered_images_cv2[i+1]), (0,0), mask=Image.open(filtered_images_cv2[i+1]))

  background.save(result_path)

  return render(request, 'fsapp/fsmain_loaded.html', {'images' : images, 'filtered_images': filtered_images, 'result' : result_path_template})

def streamA(request):
  task1 = add.delay(1,2)
  task2 = add.delay(3,4)
  task3 = add.delay(5,6)
  return render(request, 'fsapp/ssetest.html', {'task_id' : [task1.id, task2.id, task3.id]})

def streamB(request):

  if request.method == 'POST':
    # getting list of task ids and separating by commas
    unfinished_tasks = []
    finished_tasks = []
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
      #print(task)
      if not task.ready():
        #print('added task')
        unfinished_tasks.append(task)

    print(unfinished_tasks)
    # if tasks are left, pop one if ready
    if len(unfinished_tasks) > 0:
      if unfinished_tasks[0].ready():
        finished_task = unfinished_tasks[0].id
        unfinished_tasks.pop(0)
    # Return ok when all are done
    else:
      return JsonResponse({'finished_id': len(unfinished_tasks)}, safe=False, status=200) #200


    return JsonResponse({'finished_ids': finished_tasks}, safe=False, status=404) #404

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

