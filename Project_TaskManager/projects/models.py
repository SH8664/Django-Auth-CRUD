from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime

# Create your models here.

User = get_user_model()
class Project(models.Model):
    Status_Options = [('active','active'),('archived','archived')]
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=10,choices=Status_Options,default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_project_name_per_owner',
                violation_error_message="This name is already used for this owner.",
            )
        ]
    def __str__(self):
        return self.name

class Task(models.Model):
    Status_Options = [ ("todo", "Todo"),                 # (stored value, label)
    ("in_progress", "In Progress"),
    ("done", "Done"),]
    Priority_Options = [('Low','low'),('Medium','medium'),('High','high')]

    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255,null=True,blank=True)
    status = models.CharField(max_length=20,choices=Status_Options,default='todo')
    priority = models.CharField(max_length=10,choices=Priority_Options,default='low')
    due_date = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title



