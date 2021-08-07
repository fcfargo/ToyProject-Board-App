from django.db import models

# Create your models here.
class User(models.Model):
    name       = models.CharField(max_length=45)
    password   = models.CharField(max_length=200)
    email      = models.CharField(max_length=100)
    nickname   = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'