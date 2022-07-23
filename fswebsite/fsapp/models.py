import celery
from django.db import models
from django.template.defaultfilters import slugify

class Article(models.Model):
  title = models.CharField(max_length=100)
  author = models.CharField(max_length=100)
  email = models.EmailField(max_length=100)
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

class FSJob(models.Model):
  description = models.CharField(max_length=100)
  date = models.DateTimeField(auto_now_add=True)
  result = models.ImageField()

  def __str__(self):
    return self.description

def get_image_filename(instance, filename):
    title = instance.post.title
    slug = slugify(title)
    return "post_images/%s-%s" % (slug, filename) 

class FSImage(models.Model):
  image = models.ImageField()
  FSJob = models.ForeignKey(FSJob, null=True, on_delete=models.SET_NULL)

class FSFilteredImage(models.Model):
  filtered_image = models.ImageField()
  celery_task_id = models.CharField(max_length=200, default=None)
  FSJob = models.ForeignKey(FSJob, null=True, on_delete=models.SET_NULL)


