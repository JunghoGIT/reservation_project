from django.urls import path
from . import views

app_name = 'butfit'

urlpatterns = [
    path('reservation', views.create_reservation, name='reservation'),
    path('reservation/<int:pk>', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/list/<str:phone_number>', views.user_reservation_list, name='user_reservation_list'),
    path('lesson', views.create_lesson, name='create_lesson'),
]
