


from django.urls import path 
from .views import *


urlpatterns = [
    path('api/auth/register/',register,name='register'),
    path('api/auth/login/',login,name='login'),
    path('api/auth/token/refresh/',refresh,name='token_refresh'),
    path('api/auth/logout/', logout,name='logout'),
    path('api/auth/me/', profile,name='profile'),
    path('api/auth/change-password/', change_password, name='change_password'),
    # Bonus
    path('api/auth/password-reset/', password_reset, name='password_reset'),
    path('api/auth/password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
]
