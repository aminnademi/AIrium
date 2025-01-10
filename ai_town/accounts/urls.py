from django.urls import path
from .views import register, profile, main, chatbot
from .views import main, chatbot
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
    path('main/', main, name='main'),
    path('chatbot/', chatbot, name='chatbot')
]