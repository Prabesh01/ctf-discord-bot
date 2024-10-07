from django.urls import path
from . import views

urlpatterns = [
    path('submit_flag/', views.submit_flag,name='submit'),
    path('edit_challlenge_url/', views.edit_ch_link,name='edit_ch_link')
]
