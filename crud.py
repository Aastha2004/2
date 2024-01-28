#Django CRUD Application

from django import forms
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path
from django.forms import ModelForm

from django.conf import settings

settings.configure(
    DEBUG=True,
    SECRET_KEY='your-secret-key',
    ROOT_URLCONF=__name__,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.staticfiles',
    ]
)

from django.contrib import admin
from django.urls import include

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']

def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})

def task_new(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_edit.html', {'form': form})

def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_edit.html', {'form': form})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('task_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', task_list, name='task_list'),
    path('task/<int:pk>/', task_detail, name='task_detail'),
    path('task/new/', task_new, name='task_new'),
    path('task/<int:pk>/edit/', task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', task_delete, name='task_delete'),
]

# Template content
task_list_template = """
<h1>Task List</h1>
<ul>
  {% for task in tasks %}
    <li><a href="{% url 'task_detail' pk=task.pk %}">{{ task.title }}</a></li>
  {% endfor %}
</ul>
<a href="{% url 'task_new' %}">New Task</a>
"""

task_detail_template = """
<h1>{{ task.title }}</h1>
<p>{{ task.description }}</p>
<a href="{% url 'task_edit' pk=task.pk %}">Edit</a>
<a href="{% url 'task_list' %}">Back to List</a>
<form method="post" action="{% url 'task_delete' pk=task.pk %}">
  {% csrf_token %}
  <button type="submit">Delete</button>
</form>
"""

task_edit_template = """
<h1>{% if task %}Edit Task{% else %}New Task{% endif %}</h1>
<form method="post" action="{% if task %}{% url 'task_edit' pk=task.pk %}{% else %}{% url 'task_new' %}{% endif %}">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save</button>
</form>
<a href="{% url 'task_list' %}">Cancel</a>
"""

# Creating dummy request for rendering templates
from django.test import RequestFactory
request_factory = RequestFactory()
request = request_factory.get('/')

# Creating and appling migrations
from django.core.management import call_command
call_command('makemigrations')
call_command('migrate')

# Creating a superuser for admin access
call_command("createsuperuser", interactive=False, username='admin', email='admin@example.com', password='admin')

# Loading template content into the database
from django.template import Template
from django.template import Context
from django.template import TemplateDoesNotExist

try:
    Template.objects.get(name='task_list_template')
except Template.DoesNotExist:
    Template(name='task_list_template', content=task_list_template).save()

try:
    Template.objects.get(name='task_detail_template')
except Template.DoesNotExist:
    Template(name='task_detail_template', content=task_detail_template).save()

try:
    Template.objects.get(name='task_edit_template')
except Template.DoesNotExist:
    Template(name='task_edit_template', content=task_edit_template).save()

# Run the application
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['file_name.py', 'runserver'])
