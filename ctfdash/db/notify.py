import requests
from .models import Challenge, Solve, Setting
from urllib.parse import urlparse
import os, json


def get_settings(challenge):
    return Setting.objects.get(user=challenge.user)


def ordinal(n):
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    if 10 <= n % 100 <= 20:  # Special case for 11th, 12th, 13th, etc.
        suffix = 'th'
    else:
        suffix = suffixes.get(n % 10, 'th')
    return f"{n}{suffix}"


def gen_empty_embed(settings):
    webhook_json = {
        "username": settings.webhook_bot_name,
        "avatar_url": settings.webhook_bot_avatar,
    }
    webhook_json["content"]="Editing..."
    webhook_json["embeds"] = []
    webhook_json["attachments"] = []
    return webhook_json


def mask_flag(flag):
    ctf_name,flag=flag.split('{',1)
    flag=flag[:-1] # remove last }
    format=""
    for c in flag:
        if c == "_": 
            format+="_"
        elif c.isdigit():
            format+="i"
        elif c.isalpha():
            format+="c"
        else:
            format+='?'
    return ctf_name+"{"+format+"}"


def gen_challenge_embed(instance, settings):
    webhook_json = {
        "username": settings.webhook_bot_name,
        "avatar_url": settings.webhook_bot_avatar,
    }    
    embed_json = {
        "author": {
            "name": settings.embed_author_name,
            "icon_url": settings.embed_author_icon,
        },
    }    
    webhook_json["content"] = settings.new_challenge_announce_message
    embed_json["title"] = f"__{instance.title}__"
    embed_json["description"] = instance.description
    embed_json['fields'] = []
    if instance.category:
        embed_json['fields'].append({"name":"Category:","value":instance.category.name,"inline":True})
    if instance.link:
        embed_json['fields'].append({"name":"Challenge Link:","value":f"[{urlparse(instance.link).hostname}]({instance.link})","inline":True})
    if instance.author:
        embed_json['fields'].append({"name":"Author:","value":instance.author,"inline":True})
    if '{' in instance.flag and instance.flag.endswith('}'):
        embed_json['fields'].append({"name":"Flag Format:","value":mask_flag(instance.flag),"inline":False})
    files={}
    if instance.image and os.path.isfile(instance.image.path):
            image_filename = os.path.basename(instance.image.path)

            embed_json["thumbnail"] = {"url": "attachment://" + os.path.basename(instance.image.path)}
            files['file1'] = (image_filename, open(instance.image.path, 'rb'))

    footer_text=""
    if instance.is_over:
        footer_text+="🔒 • "
    if instance.disable_solve_notif:
        footer_text+="🔕 • "
    footer=settings.challenge_footer_text
    if footer_text:
        footer = footer_text+footer
    embed_json["footer"] = {"text": footer}
    webhook_json["embeds"] = [embed_json]
    if instance.attachment:
        attachment_filename = os.path.basename(instance.attachment.path)
        webhook_json["attatchments"]=[
            {
                "url": "attachment://" + attachment_filename,
                "filename":attachment_filename
            }
        ]
        files['file2'] = (attachment_filename, open(instance.attachment.path, 'rb'))
    
    return webhook_json, files


def gen_solve_embed(title,description,settings):
    webhook_json = {
        "username": settings.webhook_bot_name,
        "avatar_url": settings.webhook_bot_avatar,
    }    
    webhook_json["content"] = description +' - '+ title
    return webhook_json
    embed_json = {
        "author": {
            "name": settings.embed_author_name,
            "icon_url": settings.embed_author_icon,
        },
    }
    embed_json["title"] = f"__{title}__"
    embed_json["description"] = description
    webhook_json["embeds"] = [embed_json]
    return webhook_json


def notify_solve(challenge,userid):
    position=Solve.objects.filter(challenge=challenge).count()
    settings=get_settings(challenge)
    msg=""
    if position==1:
        pos="First"
        msg=settings.first_blood_msg_format
    elif position<=settings.top_x_priority:
        pos=ordinal(position)
        msg=settings.priority_blood_msg_format
    else: pos=str(position)
    display_solves_upto=settings.display_solves_upto    
    if display_solves_upto==0 or position<=display_solves_upto:
        if not msg: msg=settings.solved_msg_format
        msg=msg.replace("{n}",pos).replace("{xxx}",f"<@{userid}>")
        requests.post(settings.solve_webhook, json=gen_solve_embed(challenge.title, msg, settings))


def notify_challenge_add(challenge):
    settings=get_settings(challenge)
    webhook_js, files = gen_challenge_embed(challenge, settings)
    webhook_url=settings.challenge_webhook+"?wait=true"
    if files:
        payload = {'payload_json': json.dumps(webhook_js)}
        r=requests.post(webhook_url,files=files, data=payload).json()
    else:
        r=requests.post(webhook_url, json=webhook_js).json()
    Challenge.objects.filter(id=challenge.id).update(message_id=r['id'])


def edit_challenge(challenge):
    settings=get_settings(challenge)
    webhook_url=settings.challenge_webhook+"/messages/"+challenge.message_id
    requests.patch(webhook_url, json=gen_empty_embed(settings))
    webhook_js, files = gen_challenge_embed(challenge,settings)
    if files:
        payload = {'payload_json': json.dumps(webhook_js)}
        requests.patch(webhook_url, files=files, data=payload)
    else:
        requests.patch(webhook_url, json=webhook_js)
