from articles.models import Article ,Tag
from django.db import connection
from pprint import pprint 
def run():
    # many2many query 
    # article = Article.objects.filter(tags__name__icontains="dragon")
    # print(article)
    # article = article[0]
    # tag = Tag.objects.filter(article__id=f"{article.id}")
    favorited = 1 
    favorited_user_id = "admin"  # This should be a user id, not the boolean field
    # articles = Article.objects.filter(favorites__username__contains=favorited_user_id)    
    # data = {"article":{"title":"How to train your dragon", "description":"Ever wonder how?", "body":"Very carefully.", "tagList":["training", "dragons"]}}
    # data = data.get("article")
    # Article.objects.create({
        # "title": data.get("title"),
        # "description":data.get("description"),
        # "body": data.get("body"),
        # "tagList":data.get("tagList")
    # })
    # print(articles)
    # Update Article record 
    lst = []
    data = {"article":{"title":None, "body":"Very carefully.", "tagList":["training", "dragons"]}}
    data = data.get("article",{})
    for i in data:
        lst.append()
    article = Article.objects.filter(id=2).update
    print(article)
    pprint(connection.queries)
    
    