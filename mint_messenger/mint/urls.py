from django.urls import path
from django.urls import include
from django.contrib.auth.views import LoginView

from .views import *

urlpatterns = [
    path('', AccountPage.as_view(), name='account'),
    path('<int:user>', UserAccountPage.as_view(), name='user_account'),
    path('chats', Chats.as_view(), name='chats'),
    path('chats/<int:user>/', Chat.as_view(), name='messages'),
    path('chats/<int:user>/edit/<int:message>/', EditMessage.as_view(), name='edit'),
    path('friends', Friends.as_view(), name='friends'),
    path('login/', LoginView.as_view(), name='login_page'),
    path('register/', RegisterPage.as_view(), name='register_page'),
    path('forgot_password', ForgotPassword.as_view(), name='forgot_password'),
    path('forgot_password/password_change/<int:user>', PasswordChange.as_view(), name='password_change'),
    path('invite/<int:user>', send_invite, name='invite'),
    path('cancel/<int:user>', cancel_invite, name='cancel'),
    path('confirm/<int:user>', confirm_invite, name='confirm'),
    path('remove/<int:user>', remove_friend, name='remove'),
    path('delete/<int:message>', delete_message, name='delete'),

    path('api/auth/', include('rest_framework.urls'))
]
