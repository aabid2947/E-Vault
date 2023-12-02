
from django.urls import path
from .views import *


urlpatterns = [
   path('',Home,name="Home"),
   path('vault_blockchain/',vault_blockchain_view,name='vault_blockchain'),
   path('get_your_files/<str:requested_file>/',get_files,name='get_files'),
   path('login/',logIn,name='logIn'),
   path('signup/', sign_Up, name='sign_Up'),
   path('logout/',logOut,name='logout'),
   path('display_blockchain/',display_blockchain,name='display_blockchain')
]