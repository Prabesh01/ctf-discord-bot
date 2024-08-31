from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from db.models import Challenge, Solve
from django.utils import timezone
from config import get_config
from functools import wraps

def api_key_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        provided_api_key = request.headers.get('X-API-Key', '')
        if provided_api_key != get_config('API_KEY'):
            return HttpResponse("Unauthorized", status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

@csrf_exempt
@api_key_required
def submit_flag(request):
    if request.method == 'POST':
        provided_api_key = request.headers.get('X-API-Key')
        if provided_api_key != get_config('API_KEY'):
            return HttpResponse("", status=403)
        challenge_id = request.POST.get('challenge')
        userid = request.POST.get('user')
        if userid and challenge_id:
            user, created = User.objects.get_or_create(username=userid)

            try:
                challenge = Challenge.objects.get(id=challenge_id)
            except Challenge.DoesNotExist:
                return HttpResponse("", status=404)

            # check if challenge is over
            if challenge.is_over:
                return HttpResponse("", status=400)
            solve, created = Solve.objects.get_or_create(
                challenge=challenge,
                user=user,
                defaults={'solved_time': timezone.now()}
            )
            if created: return HttpResponse("", status=200)
            return HttpResponse("", status=202)
    return HttpResponse("", status=400)

@csrf_exempt
@api_key_required
def get_challenges(request):
    challenges = Challenge.objects.filter(is_over=False).order_by('-add_time')[:10].values('id', 'title', 'flag')
    return HttpResponse(challenges)