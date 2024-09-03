from django.db import models
from django.contrib.auth.models import User
from .validators import get_file_path, get_image_path, attatchment_validate, image_validate
from django.core.validators import FileExtensionValidator

class Setting(models.Model):
    challenge_webhook = models.URLField(max_length=500, blank=False, null=False, help_text="Webhook URL to send new challenge notifications")
    solve_webhook = models.URLField(max_length=500, blank=False, null=False, help_text="Webhook URL to send challenge solve notifications")
    new_challenge_announce_message = models.TextField(default='New Challenge is out! @everyone', help_text="Message to send when a new challenge is posted")
    first_blood_msg_format = models.TextField(default='First Blood by {xxx} :drop_of_blood: :space_invader:', help_text="Message to send when a user solves a challenge first")
    top_x_priority = models.PositiveIntegerField(default=3, help_text="Use priority_blood_msg_format for top X solvers")
    priority_blood_msg_format = models.TextField(default='{n} Blood {xxx} :fire: :drop_of_blood:', help_text="{n} is replaced by the rank of the solver and {xxx} is replaced by the solver's ping")
    display_solves_upto = models.PositiveIntegerField(default=0, help_text="stop notifying after n solves, 0 for infinite")
    solved_msg_format = models.TextField(default='{n}. {xxx} solved 🫡', help_text="{xxx} is replaced by the solver's ping and {n} is replaced by rank")
    webhook_bot_name = models.CharField(max_length=50, default='Conan', help_text="Name of the bot to use in announcements") 
    webhook_bot_avatar = models.URLField(max_length=500, default="https://cdn.discordapp.com/avatars/1280495542941647000/a9282d721adfeabf0b15a91459daa75d.webp", help_text="Avatar of the bot")
    embed_author_name = models.CharField(max_length=50, default='CTF', help_text="Name of embeds message author")
    embed_author_icon = models.URLField(max_length=500, default="https://capturetheflag.withgoogle.com/img/Flag.png", help_text="Icon of the author")
    challenge_footer_text = models.CharField(max_length=200, default='Submit flag to Conan bot using slash command `/flag`', help_text="Footer text for the challenge embed")       
    user = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE,editable=False)
    def __str__(self):
        return self.title

class Solve(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} solved {self.challenge.title}'
