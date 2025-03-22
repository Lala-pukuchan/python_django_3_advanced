from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, ListView, DetailView, CreateView, FormView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

from .models import Article, UserFavouriteArticle

# ------------------------------------------------
# Exercise 00
# ------------------------------------------------

class HomeRedirectView(RedirectView):
    # ルート('/')にアクセスされたら articles へリダイレクト
    pattern_name = 'articles'


class ArticleListView(ListView):
    """全 Article をテーブル表示(タイトル, 著者, 作成日時, synopsis など)
       ※ content だけは一覧で表示しない
    """
    # used model is Article
    model = Article
    # it will display article_list.html
    template_name = 'articles/article_list.html'
    # the data will be stored in articles and can be accessed in the template
    context_object_name = 'articles'

    # 新しいもの順に並び替えたい場合:
    ordering = ['-created']  # もしくは filter や override get_queryset

    # ListView では、標準で object_list に記事一覧が入るが
    # ここでは context_object_name='articles' としてアクセスできるように。

    # ※synopsis は課題で312字, テーブル表示など


# LoginView is inherited from AuthenticationForm
# username and password are the default fields
class MyLoginView(LoginView):
    """ログイン画面 (Exercise 00)
       エラー時はテンプレート内でエラーを出す。
       成功時は 'home' にリダイレクトする。
    """
    # display login_form.html
    template_name = 'articles/login_form.html'
    # redirect to home if user is already authenticated
    redirect_authenticated_user = True

    # when user is authenticated, redirect to home
    def get_success_url(self):
        return reverse('home')  # ログイン成功時: Home(= / ) へ

    # デフォルトで django.contrib.auth.forms.AuthenticationForm を使用
    # エラーは form.non_field_errors 等で取得可能


# ------------------------------------------------
# Exercise 01
# ------------------------------------------------

class PublicationsListView(LoginRequiredMixin, ListView):
    """ログイン中のユーザーが「自分が author の記事のみ」表示する
       fields: title, synopsis, created
    """
    # model = Article  # これだけだと全記事が表示される
    model = Article
    # it will display publications_list.html
    template_name = 'articles/publications_list.html'
    # the data will be stored in articles and can be accessed in the template
    context_object_name = 'articles'

    login_url = reverse_lazy('login')  # ログインしていないときはここへ飛ばす

    def get_queryset(self):
        # 自分の投稿のみフィルタリング
        qs = super().get_queryset()
        return qs.filter(author=self.request.user).order_by('-created')


class ArticleDetailView(DetailView):
    """特定の記事(Article)の詳細を表示する (URLにpkを含む)
       fields: 全項目(title, author, created, synopsis, content)
    """
    # get article queried by pk which is passed in the URL
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'


class MyLogoutView(LogoutView):
    """ログアウト用: 成功したらHomeへ"""
    next_page = reverse_lazy('home')


class FavouritesListView(LoginRequiredMixin, ListView):
    """ログイン中ユーザーのお気に入りの記事タイトルを一覧表示
       記事タイトルをリンクにして Detail に飛べるようにする
    """
    model = UserFavouriteArticle
    template_name = 'articles/favourites_list.html'
    context_object_name = 'favourites'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        # 自分のお気に入りのみ
        qs = super().get_queryset()
        return qs.filter(user=self.request.user).select_related('article')


# ------------------------------------------------
# Exercise 02
# ------------------------------------------------

# 1) Register(新規ユーザー作成)用フォーム
User = get_user_model()

class RegisterForm(forms.ModelForm):
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password_confirm")
        if p1 != p2:
            self.add_error("password_confirm", "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_password = self.cleaned_data["password"]
        user.set_password(raw_password)  # ハッシュ化
        if commit:
            user.save()
        return user


class RegisterView(CreateView):
    """未ログインユーザーがアカウント作成する (Exercise 02)"""
    form_class = RegisterForm
    template_name = 'articles/register_form.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        # 既にログインしている場合はアクセス禁止/リダイレクト
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


# 2) Publish(Article作成)用: CreateView
class PublishView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = 'articles/publish_form.html'
    fields = ('title', 'synopsis', 'content')  
    # author はフォームに出さない

    login_url = reverse_lazy('login')
    success_url = reverse_lazy('publications')  # 作成したら自分の投稿一覧へ

    def form_valid(self, form):
        # authorフィールドは現在ログインしているUserに自動セット
        form.instance.author = self.request.user
        return super().form_valid(form)


# 3) Add to Favourite: CreateViewでUserFavouriteArticleに追加
class AddFavouriteView(LoginRequiredMixin, CreateView):
    model = UserFavouriteArticle
    fields = []  # POSTフォーム上、表示要素はなし
    template_name = 'articles/add_favourite_form.html'
    success_url = reverse_lazy('favourites')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        # URLのpkからArticleを取得
        article_id = self.kwargs['pk']
        article_obj = Article.objects.get(pk=article_id)
        # user と article を紐付け
        form.instance.user = self.request.user
        form.instance.article = article_obj
        return super().form_valid(form)

    # 同じ記事を重複登録させたくない場合はバリデーションでチェックしてもOK
    def post(self, request, *args, **kwargs):
        article_id = self.kwargs['pk']
        if UserFavouriteArticle.objects.filter(user=request.user, article_id=article_id).exists():
            # すでにお気に入り済みなら弾く例
            return redirect('favourites')
        return super().post(request, *args, **kwargs)
