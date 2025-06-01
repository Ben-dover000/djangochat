from django.urls import path
from . import views

urlpatterns = [
    path('', views.rooms, name='rooms'),
    path('create/', views.create_room, name='create_room'),
    
    # URLs de convite
    path('invites/', views.convite_pendente, name='convite_pendente'),
    path('invites/accept/<int:invitation_id>/', views.accept_invite, name='accept_invite'),
    path('invites/reject/<int:invitation_id>/', views.reject_invite, name='reject_invite'),
    path('invite/<int:user_id>/', views.invite_user, name='invite_user'),
    
    # URLs das salas
    path('rooms/<slug:room_slug>/kick/<int:user_id>/', views.kick_user, name='kick_user'),
    path('rooms/<slug:slug>/', views.room_detail, name='room_detail'),
    
    # Por analizar
    path('<slug:slug>/', views.room_detail, name='room_detail'),
]