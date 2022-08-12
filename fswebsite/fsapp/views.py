import os
import cv2
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import FSJob, FSImage
from .tasks import add
from .fsprocessor import FSProcessor, align_images, focus_stack
from django.core.files import File
from django.conf import settings
import json
from PIL import Image

def fsjob_form(request):
  print('in view function')
  if request.method == 'POST':
    if 'first form' in request.POST:
      print('this was from the first form')
      data = request.POST
      images = request.FILES.getlist('images')
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

  if not job.is_finished:
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

    return render(request, 'fsapp/fsmain.html', {'images' : images, 'task_ids' : celery_task_ids, 'job_id':id, 'taskid_img_dict': json.dumps(taskid_img_dict) })
  else:
    return render(request, 'fsapp/fsmain_loading.html', {'jobid' : id})

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

    # if task not done, add it to the unfinished list
    for i in range(len(post_list_cleaned)):
      task = add.AsyncResult(post_list_cleaned[i])
      if not task.ready():
        unfinished_tasks.append(task)
      else:
        finished_tasks.append(task.id)

    print(finished_tasks)
    # if tasks are left, pop one if ready
    if len(unfinished_tasks) > 0:
      if unfinished_tasks[0].ready():
        unfinished_tasks.pop(0)
    # Return ok when all are done
    else:
      return JsonResponse({'finished_tasks': finished_tasks}, safe=False, status=200) #200 Done


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
  job.is_finished = True
  job.save()

  return render(request, 'fsapp/fsmain_loaded.html', {'images' : images, 'filtered_images': filtered_images, 'result' : result_path_template})



