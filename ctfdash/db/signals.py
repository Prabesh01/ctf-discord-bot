from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Challenge, Solve, Setting
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .notify import notify_solve, notify_challenge_add, edit_challenge
from django.utils import timezone
import os
from django.contrib.auth.models import Permission


@receiver(post_save, sender=Solve)
def solve_post_save(sender, instance, created, **kwargs):
    if created:
        challenge = instance.challenge
        challenge.solve_count+=1 # Solve.objects.filter(challenge=challenge).count()
        challenge.save()
        # check if is_notif_disabled or challenge over
        if challenge.disable_solve_notif==False and challenge.is_over==False:
            notify_solve(challenge,instance.user.username)


@receiver(pre_save, sender=Challenge)
def challenge_pre_save(sender, instance, **kwargs):
    if instance.id: 
        previous = Challenge.objects.get(id=instance.id)
        changed_fields = [field for field in model_to_dict(instance) if getattr(instance, field) != getattr(previous, field)]
        if instance.attachment!=previous.attachment:
                        if previous.attachment and os.path.isfile(previous.attachment.path):
                                os.remove(previous.attachment.path)
        if instance.image!=previous.image:
                        if previous.image and os.path.isfile(previous.image.path):
                                os.remove(previous.image.path)
        if any([field in changed_fields for field in ['title', 'description', 'category', 'author', 'link', 'attachment', 'image','disable_solve_notif', 'flag', 'is_over']]):            
            if previous.is_over and not instance.is_over:
                if instance.message_id:
                    instance._edit_challenge = True
                else:
                    instance._notify_add = True

            elif instance.message_id:
                instance._edit_challenge = True
            else:
                # cant edit challenge that is not posted and has no message_id
                pass


@receiver(post_save, sender=Challenge)
def challenge_post_save(sender, instance, created, **kwargs):
    if created and not instance.is_over:
        notify_challenge_add(instance)
    elif hasattr(instance, '_notify_add'):
        Challenge.objects.filter(id=instance.id).update(add_time=timezone.now())
        notify_challenge_add(instance)
    elif hasattr(instance, '_edit_challenge'):
        edit_challenge(instance)


@receiver(post_delete, sender=Challenge)
def challenge_post_delete(sender, instance, **kwargs):
    if instance.attachment:
        if os.path.isfile(instance.attachment.path):
            os.remove(instance.attachment.path)
    
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if instance.is_staff and instance.username != 'admin':
        Setting.objects.get_or_create(user=instance)
        permissions = Permission.objects.filter(name__in=[
             "Can change user",
             "Can delete user",
             "Can view user",
             "Can add category",
             "Can change category",
             "Can delete category",
             "Can view category",
             "Can add challenge",
             "Can change challenge",
             "Can delete challenge",
             "Can view challenge",
             "Can change setting",
             "Can view setting",
             "Can delete solve",
             "Can view solve"])
        instance.user_permissions.add(*permissions)
