from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from db.models import Challenge, Solve
from django.utils import timezone
from config import get_config
from functools import wraps
from django.http import JsonResponse

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
        flag = request.POST.get('flag')
        title_partial = request.POST.get('challenge')
        userid = request.POST.get('user')

        if userid and flag:            
            # check if challenge exists
            challenge=None
            active_challenges=Challenge.objects.filter(is_over=False).order_by('-add_time').values('id', 'title', 'flag')
            if title_partial:
                for c in active_challenges:
                    title=c['title']
                    if title.lower().startswith(title_partial.lower()):
                        challenge = c
                        break
            else: 
                challenge = active_challenges.first()

            if not challenge: return HttpResponse(f"Challenge doesn't exist!", status=404)
            title=challenge['title']

            # check if flag is correct
            if flag.lower() != challenge['flag'].lower():
                return HttpResponse("Incorrect! - "+title, status=422)
            
            # Create User if not exist
            user, created = User.objects.get_or_create(username=userid)

            # create a new Solve object if not exist
            _, created = Solve.objects.get_or_create(
                challenge=Challenge.objects.get(id=challenge['id']),
                user=user,
                defaults={'solved_time': timezone.now()}
            )
            if created: return HttpResponse("Correct! - "+title, status=200) # Correct Flag
            return HttpResponse("Correct! I said the same last time - "+title, status=202) # Already Solved
        else: return HttpResponse("", status=400) # Parameter Missing

    return HttpResponse("", status=405) # Method Not Allowed
