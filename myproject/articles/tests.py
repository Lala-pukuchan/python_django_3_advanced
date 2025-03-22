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
        # ログインしてない状態で favourites, publications, publish にアクセス → ログイン画面にリダイレクト
        resp = self.client.get(reverse('favourites'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

        resp = self.client.get(reverse('publications'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

        resp = self.client.get(reverse('publish'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_register_inaccessible_when_logged_in(self):
        # ログイン後は Register ページへ行けない/リダイレクト
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('register'))
        self.assertEqual(resp.status_code, 302)  # home へ飛ばすなど
    
    def test_add_favourite_duplicate(self):
        self.client.login(username='testuser', password='12345')
        # 1回目: 成功
        url = reverse('add_favourite', args=[self.article.pk])
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 302)  # favouritesへリダイレクト
        self.assertEqual(UserFavouriteArticle.objects.count(), 1)

        # 2回目: 同じ記事を再度登録 → 失敗 (弾いているなら件数は変わらない)
        resp = self.client.post(url, {})
        self.assertEqual(UserFavouriteArticle.objects.count(), 1)
