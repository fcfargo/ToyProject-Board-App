from django.db             import models

# Create your models here.
class BoardCategory(models.Model):
    name       = models.CharField(max_length=45)
    
    class Meta:
        db_table = 'board_categories'

class PostCategory(models.Model):
    name       = models.CharField(max_length=45)
    
    class Meta:
        db_table = 'post_categories'

class Post(models.Model):
    board_category = models.ForeignKey('BoardCategory', on_delete=models.SET_NULL, null=True)
    user           = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post_category  = models.ForeignKey('PostCategory', on_delete=models.SET_NULL, null=True)
    title          = models.CharField(max_length=200)
    content        = models.TextField()
    views          = models.IntegerField(default=0)
    ip_address     = models.GenericIPAddressField(default='192.168.0.1')
    password       = models.CharField(max_length=200)
    group_id       = models.BigIntegerField()
    group_order    = models.IntegerField(default=0)
    group_depth    = models.IntegerField(default=0)
    tag            = models.ManyToManyField('Tag', through='PostTag')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'

class FileUpload(models.Model):
    post          = models.ForeignKey('Post', on_delete=models.CASCADE)
    title         = models.CharField(max_length=500)
    path          = models.FileField(upload_to='media/', null=True)
    
    class Meta:
        db_table = 'file_uploads'

class PostTag(models.Model):
    post         = models.ForeignKey('Post', on_delete=models.CASCADE)
    tag          = models.ForeignKey('Tag', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'post_tags'

class Tag(models.Model):
    name         = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'tags'