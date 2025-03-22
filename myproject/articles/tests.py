from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Article, UserFavouriteArticle

class ArticlesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

        self.article = Article.objects.create(
            title="Test Article",
            author=self.user,
            synopsis="Lorem ipsum",
            content="Body content"
        )

    def test_login_required_views(self):
        # ログインしていない状態で以下のページにアクセス
        resp = self.client.get(reverse('favourites'))
        self.assertEqual(resp.status_code, 302)  # 302はリダイレクトを意味する
        self.assertIn(reverse('login'), resp.url)  # ログインページにリダイレクトされることを確認

        # publicationsページも同様にテスト
        resp = self.client.get(reverse('publications'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

        # publishページも同様にテスト
        resp = self.client.get(reverse('publish'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_register_inaccessible_when_logged_in(self):
        # ログイン
        self.client.login(username='testuser', password='12345')
        # 登録ページにアクセス試行
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 302)  # ホームページにリダイレクトされることを確認
    
    def test_add_favourite_duplicate(self):
        self.client.login(username='testuser', password='12345')
        # 1回目: お気に入りに追加（成功）
        url = reverse('add_favourite', args=[self.article.pk])
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 302)  # リダイレクト（成功）
        self.assertEqual(UserFavouriteArticle.objects.count(), 1)  # お気に入り数が1つ

        # 2回目: 同じ記事を追加（失敗）
        resp = self.client.post(url, {})
        self.assertEqual(UserFavouriteArticle.objects.count(), 1)  # お気に入り数は変わらない
