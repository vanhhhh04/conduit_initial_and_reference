from django.urls import path
from. import views  

urlpatterns = [
    path('users', views.user_register, name="regiser_user"),
    path('users/login', views.user_login, name="login_user" ),
    path('user', views.get_and_update_user, name="get_update_user" ),
    path('profiles/<str:username>', views.get_profiles, name="get_profiles"),
    path('profiles/<str:username>/follow', views.follow_unfollow_user, name="follow_unfollow_user"),
    # path('user', views.get_or_update_user, name="get_or_update_user"),
    # path('profiles/<str:username>', views.get_profile, name="get_profile"),
]