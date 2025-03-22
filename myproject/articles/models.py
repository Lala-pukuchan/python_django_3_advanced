from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    #    Article テーブル:
    #id | title | author_id
    #1  | 記事1  | 1        # ユーザー1が作成
    #2  | 記事2  | 2        # ユーザー2が作成
    title = models.CharField(max_length=64, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created = models.DateTimeField(auto_now_add=True, null=False)
    synopsis = models.CharField(max_length=312, null=False)
    content = models.TextField(null=False)

    def __str__(self):
        return self.title


class UserFavouriteArticle(models.Model):
    #    UserFavouriteArticle テーブル:
    #id | user_id | article_id
    #1  | 1       | 2         # ユーザー1が記事2をお気に入り
    #2  | 2       | 1         # ユーザー2が記事1をお気に入り
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)

    def __str__(self):
        # Article の title を返す
        return self.article.title
