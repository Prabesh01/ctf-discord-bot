from config import get_config
import requests
from .models import Challenge, Solve
from urllib.parse import urlparse
import os, json

webhook_json = {
    "username": get_config("webhook_bot_name"),
    "avatar_url": get_config("webhook_bot_avatar"),
}
embed_json = {
    "author": {
        "name": get_config("embed_author_name"),
        "icon_url": get_config("embed_author_avatar"),
    },
}

def ordinal(n):
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    if 10 <= n % 100 <= 20:  # Special case for 11th, 12th, 13th, etc.
        suffix = 'th'
    else:
        suffix = suffixes.get(n % 10, 'th')
    return f"{n}{suffix}"

def gen_empty_embed():
    webhook_json = {
        "username": get_config("webhook_bot_name"),
        "avatar_url": get_config("webhook_bot_avatar"),
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


def gen_challenge_embed(instance):
    webhook_json["content"] = get_config("announce_new_challenge_message")
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
    if instance.attachment:
        pass    
    files={}
    if instance.image and os.path.isfile(instance.image.path):
            image_filename = os.path.basename(instance.image.path)

            embed_json["image"] = {"url": "attachment://" + os.path.basename(instance.image.path)}
            files['file'] = (image_filename, open(instance.image.path, 'rb'))

    footer_text=""
    if instance.is_over:
        footer_text+="🔒 • "
    if instance.disable_solve_notif:
        footer_text+="🔕 • "
    footer=get_config("new_challenge_footer_text")
    if footer_text:
        footer = footer_text+footer
    embed_json["footer"] = {"text": footer}
    webhook_json["embeds"] = [embed_json]
    
    return webhook_json, files


def gen_solve_embed(title,description):
    webhook_json = {
        "username": get_config("webhook_bot_name"),
        "avatar_url": get_config("webhook_bot_avatar"),
    }    
    webhook_json["content"] = description +' - '+ title
    return webhook_json
    embed_json = {
        "author": {
            "name": get_config("embed_author_name"),
            "icon_url": get_config("embed_author_avatar"),
        },
    }
    embed_json["title"] = f"__{title}__"
    embed_json["description"] = description
    webhook_json["embeds"] = [embed_json]
    return webhook_json


def notify_solve(challenge,userid):
    position=Solve.objects.filter(challenge=challenge).count()
    msg=""
    if position==1:
        pos="First"
        msg=get_config('first_blood_msg_format')
    elif position<=get_config('top_x_priority'):
        pos=ordinal(position)
        msg=get_config('priority_blood_msg_format')
    else: pos=str(position)
    display_solves_upto=get_config('display_solves_upto')    
    if display_solves_upto==0 or position<=get_config('display_solves_upto'):
        if not msg: msg=get_config('solved_msg_format')
        msg=msg.replace("{n}",pos).replace("{xxx}",f"<@{userid}>")
        requests.post(get_config('solves_notif_channel_webhook'), json=gen_solve_embed(challenge.title, msg))


def notify_challenge_add(challenge):
    webhook_js, files = gen_challenge_embed(challenge)
    webhook_url=get_config('challenge_announce_channel_webhook')+"?wait=true"
    if files:
        payload = {'payload_json': json.dumps(webhook_json)}
        r=requests.post(webhook_url,files=files, data=payload).json()
    else:
        r=requests.post(webhook_url, json=webhook_js).json()
    Challenge.objects.filter(id=challenge.id).update(message_id=r['id'])


def edit_challenge(challenge):
    webhook_url=get_config('challenge_announce_channel_webhook')+"/messages/"+challenge.message_id
    requests.patch(webhook_url, json=gen_empty_embed())
    webhook_js, files = gen_challenge_embed(challenge)
    if files:
        payload = {'payload_json': json.dumps(webhook_json)}
        requests.patch(webhook_url, files=files, data=payload)
    else:
        requests.patch(webhook_url, json=webhook_js)
