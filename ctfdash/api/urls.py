from django.urls import path
from . import views

urlpatterns = [
    path('submit_flag/', views.submit_flag,name='submit'),
    path('get_challenges/', views.get_challenges,name='list'),

]