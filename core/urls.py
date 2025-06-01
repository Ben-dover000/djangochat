from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import album_list

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('mudar_palavra-passe/', auth_views.PasswordChangeView.as_view(template_name='registos/mudar_palavra-passe.html'), name='password_change'),
    path('mudar_palavra-passe/concluido/', auth_views.PasswordChangeDoneView.as_view(template_name='registos/mudar_palavra-passe_concluido.html'), name='password_change_done'),
    path('album/<int:id_album>/', views.album_detail, name='album_detail'),
    path('album/<int:id_album>/favorito/', views.toggle_album_favorito, name='toggle_album_favorito'),
    path('artista/<int:id_artista>/', views.artista_detail, name='artista_detail'),
    path('artista/<int:id_artista>/favorito/', views.toggle_artista_favorito, name='toggle_artista_favorito'),
    path('utilizador/<int:user_id>/', views.user_info_view, name='user_info'),
    path('pesquisar/', views.pesquisa, name='pesquisar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    