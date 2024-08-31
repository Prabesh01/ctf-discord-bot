from django.db import models
from django.contrib.auth.models import User
from .validators import get_file_path, get_image_path, attatchment_validate, image_validate
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

ALLOWED_IMAGE_EXTENSIONS=['jpg', 'png', 'jpeg', 'webp']
class Challenge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    attachment = models.FileField(upload_to=get_file_path, blank=True, null=True,validators=[attatchment_validate])
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True,validators=[image_validate, FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)])
    flag = models.CharField(max_length=255)
    disable_solve_notif = models.BooleanField(default=False)
    is_over = models.BooleanField(default=False)
    message_id = models.CharField(max_length=50, blank=True, null=True, editable=False)
    add_time = models.DateTimeField(auto_now_add=True, editable=False)
    solve_count = models.IntegerField(default=0,editable=False)

    def __str__(self):
        return self.title

class Solve(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} solved {self.challenge.title}'
