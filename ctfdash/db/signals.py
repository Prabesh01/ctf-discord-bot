from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Challenge, Solve
from django.forms.models import model_to_dict
from .notify import notify_solve, notify_challenge_add, edit_challenge
from config import get_config
import json

def ask_bot_to_update_challenges():
    with open(get_config('COMM_FILE_PATH'),'w') as f:
        challenges = Challenge.objects.filter(is_over=False).order_by('-add_time')[:10].values('id', 'title', 'flag')
        json.dump({'challenges': list(challenges)},f)

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
        if any([field in changed_fields for field in ['title', 'description', 'category', 'author', 'link', 'attachment', 'image','disable_solve_notif', 'is_over']]):            
            if previous.is_over and not instance.is_over:
                # notify that challenge is back
                # notify_challenge_add(instance)
                instance._notify_add = True
                # clear past solves?

            elif instance.message_id:
                # edit_challenge(instance)
                instance._edit_challenge = True
            else:
                # cant edit challenge that is not posted and has no message_id
                pass


@receiver(post_save, sender=Challenge)
def challenge_post_save(sender, instance, created, **kwargs):
    # if created:
    #     if instance.is_over:
    #         # no need to notify. just return
    #         return
    #     notify_challenge_add(instance)
    if created and not instance.is_over:
        notify_challenge_add(instance)
        ask_bot_to_update_challenges()
    elif hasattr(instance, '_notify_add'):
        notify_challenge_add(instance)
        ask_bot_to_update_challenges()
    elif hasattr(instance, '_edit_challenge'):
        edit_challenge(instance)
        ask_bot_to_update_challenges()
