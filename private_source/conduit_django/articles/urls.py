from django.urls import path
from. import views  

urlpatterns = [
    path('articles', views.list_and_create_articles, name="list_and_create_articles"),
    path('articles/feed', views.list_favorited_articles, name="list_favorited_articles"),
    path('articles/<slug:slug>', views.get_and_update_and_delete_article, name="get_update_delete_article"),
    path('articles/<slug:slug>/favorite', views.favorite_unfavorite_article, name="favorite_and_unfavorite_article"),
    path('tags', views.list_tag, name="list_tag"),
]
