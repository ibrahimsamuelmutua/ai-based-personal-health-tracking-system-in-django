from django.urls import path
from .views import home,signup,login_user

urlpatterns = [
    path('',home, name='home-url'),
    path('signup/', signup, name='signup-url'),
    path('login/', login_user, name='login-url'),
]