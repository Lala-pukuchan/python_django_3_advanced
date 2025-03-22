from django.contrib.auth.forms import AuthenticationForm

def login_form(request):
    """未ログインユーザーにログインフォームを提供するコンテキストプロセッサー"""
    if not request.user.is_authenticated:
        return {'login_form': AuthenticationForm()}
    return {'login_form': None} 