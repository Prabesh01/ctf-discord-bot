from django.shortcuts import render
from django.shortcuts import redirect
from config import get_config
import requests
from django.contrib.auth import login as l
from django.contrib.auth.models import User

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = get_config('DISCORD_CLIENT_ID')
CLIENT_SECRET = get_config('DISCORD_CLIENT_SECRET')
web_url=get_config('django_web_url')
REDIRECT_URI = web_url+'/login'
OAUTH_URL=f'https://discord.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&scope=guilds&redirect_uri={REDIRECT_URI}&prompt=consent&integration_type=0'

def exchange_code(code):
  data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
  if r.status_code != 200:
    return None
  return r.json()


def get_guilds(acess):
    guild_data=requests.get('%s/users/@me/guilds' % API_ENDPOINT,headers={"Authorization": "Bearer "+acess})
    if guild_data.status_code!=200:
        return False
    guild_data=guild_data.json()

    own_guilds={}
    for guild in guild_data:
        if guild['owner']: own_guilds[guild['id']]=[guild['name'],guild['icon']]
    return own_guilds

def login(request):
    if request.user.username:
        return redirect('/admin/') 
    code = request.GET.get('code', None)
    token = request.GET.get('token', None)
    id=request.GET.get('id', None)
    if token and id:
        double_check=get_guilds(token)
        if id in double_check:
            user,_ = User.objects.get_or_create(username=id)
            user.is_staff=True
            user.save()
            l(request, user)
            return redirect("/admin", permanent=False)
        else:
           return render(request, 'login.djhtml', {'error': 'Something went wrong. Please try again.',"login":OAUTH_URL})
    if code:
        token_response=exchange_code(code)
        if not token_response or not 'access_token' in token_response:
            return render(request, 'login.djhtml', {'error': 'Something went wrong. Please try again.',"login":OAUTH_URL})
        guild_data=get_guilds(token_response['access_token'])
        if not guild_data:
           return render(request, 'login.djhtml', {'error': 'You have to be owner of atleast one guild to continue.',"login":OAUTH_URL})
        return render(request, 'login.djhtml', {"guilds":guild_data,"token":token_response['access_token']})

        # return render(request, 'login.html', {'next': request.GET.get('next')})
    return redirect(OAUTH_URL, permanent=False)


def home(request):
  return render(request, 'home.djhtml', {'id':CLIENT_ID,"login":OAUTH_URL, "dashboard":web_url})