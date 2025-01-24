from django.urls import path
from .views import register, main, chatbot
from .views import main, chatbot, getHistory, chatbot_together
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('main/', main, name='main'),
    path('chatbot/', chatbot, name='chatbot'),
    path('getHistory/', getHistory, name='get-history'),
    path('chatbot-together/', chatbot_together, name='chatbot-together'),
]