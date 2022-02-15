from django.urls import path
from . import views
from django.contrib.auth import logout

app_name = 'accounts'

urlpatterns = [
    path('credit', views.credit, name='credit'),
    path('credit/<int:user_pk>',views.credit_detail, name='credit_detail'),
    path('', views.UserCreate.as_view()),
    path('logout/', views.logout, name='logout'),

]
