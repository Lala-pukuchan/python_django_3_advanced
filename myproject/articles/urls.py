from django.urls import path
from . import views

urlpatterns = [
    # Exercise 00
    path('', views.HomeRedirectView.as_view(), name='home'),           # ルート(ホーム) → Articlesへリダイレクト
    path('articles/', views.ArticleListView.as_view(), name='articles'),
    path('login/', views.MyLoginView.as_view(), name='login'),

    # Exercise 01
    path('publications/', views.PublicationsListView.as_view(), name='publications'),
    path('detail/<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('favourites/', views.FavouritesListView.as_view(), name='favourites'),

    # Exercise 02
    path('register/', views.RegisterView.as_view(), name='register'),
    path('publish/', views.PublishView.as_view(), name='publish'),
    path('add-favourite/<int:pk>/', views.AddFavouriteView.as_view(), name='add_favourite'),

    # 以降 bootstrap (ex04) / i18n (ex05) / tests (ex06) を反映
]
