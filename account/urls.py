from django.urls import path
from rest_framework_jwt.views import refresh_jwt_token
from account.utils import NewObtainJSONWebToken
from account.views import RegistrationView, RegistrationTokenView, PasswordForgetCodeView, ResetTokenView, ProfileView, \
    UserDeleteView, UserStatus, UserListView, UserDetailView, logout_user

urlpatterns = [
    path('login/', NewObtainJSONWebToken.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('refresh/', refresh_jwt_token, name='refresh'),
    path('status/', UserStatus.as_view(), name='status'),
    path('register/', RegistrationView.as_view(), name='registration'),
    path('register/token/', RegistrationTokenView.as_view(), name='registration-token'),
    path('password/reset/', PasswordForgetCodeView.as_view(), name='password-reset'),
    path('password/reset/code/', ResetTokenView.as_view(), name='token-reset'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('delete/', UserDeleteView.as_view(), name='user-delete'),
    path('user/list/', UserListView.as_view(), name='user-list'),
    path('user/detail/<int:id>/', UserDetailView.as_view(), name='user-detail'),
]
