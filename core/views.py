from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Album, Artist
from .forms import CriarConta
from random import shuffle
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PerfilForm
from .models import Perfil

from django.db.models import Q

def pesquisa(request):
    query = request.GET.get('q', '').strip()

    artist_results = []
    perfil_results = []

    if query:
        artist_results = Artist.objects.filter(nome__icontains=query)
        perfil_results = Perfil.objects.filter(
            Q(user__username__icontains=query)
        ).select_related('user')

    context = {
        'query': query,
        'artist_results': artist_results,
        'perfil_results': perfil_results,
    }
    return render(request, 'core/resultado_pesquisa.html', context)


@login_required
def user_info_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    return render(request, 'core/user_info.html', {'user_obj': user_obj})


def frontpage(request):
    albums = Album.objects.all() #Busca todos os álbuns da base de dados
    albums = list(albums)  # Converte a queryset para uma lista
    shuffle(albums)  # Aleatôriamente pega os álbuns
    albums = albums[:8]  #Apresenta apenas os primeiros 
    artistas = Artist.objects.all()  # Busca todos os artistas da base de dados
    artistas = list(artistas)  # Converte a queryset para lista
    shuffle(artistas)  # Aleatoriza os artistas
    artistas = artistas[:8]  # Apresenta os primeiros 8 artistas
    return render(request, 'core/frontpage.html', {'albums': albums, 'artistas': artistas})  #Manda os resultados (Artistas e Albuns) para a frontpage


def signup(request):
    if request.method == 'POST':
        form = CriarConta(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = CriarConta()
    
    return render(request, 'core/signup.html', {'form': form})


@login_required
def perfil_view(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)

    favoritos_artista = request.user.artista_favorito.all()
    favoritos_album = request.user.album_favorito.all()

    return render(request, 'core/perfil.html', {
        'perfil_form': form,
        'favoritos_artistas': favoritos_artista,
        'favoritos_albuns': favoritos_album,
    })

def album_list(request):
    albums = Album.objects.all()
    return render(request, 'core/lista.html', {'albums': albums})

def listar_artistas(request):
    artistas = Artist.objects.all()
    return render(request, 'core/frontpage.html', {'artistas': artistas})

def artista_detail(request, id_artista):
    artista = get_object_or_404(Artist, id_artista=id_artista)

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = artista.favorito.filter(id=request.user.id).exists()

    return render(request, 'core/artista_detail.html', {
        'artista': artista,
        'is_favorited': is_favorited,
    })

def album_detail(request, id_album):
    album = get_object_or_404(Album, id_album=id_album)
    return render(request, 'core/album_detail.html', {'album': album})

@login_required
def toggle_artista_favorito(request, id_artista):
    artista = get_object_or_404(Artist, pk=id_artista)
    if request.user in artista.favorito.all():
        artista.favorito.remove(request.user)
    else:
        artista.favorito.add(request.user)
        return redirect('artista_detail', id_artista=artista.pk)
    return redirect('artista_detail', id_artista=id_artista)


@login_required
def toggle_album_favorito(request, id_album):
    album = get_object_or_404(Album, pk=id_album)
    if request.user in album.favorito.all():
        album.favorito.remove(request.user)
    else:
        album.favorito.add(request.user)
        return redirect('album_detail', id_album=album.pk)
    return redirect('album_detail', id_album=id_album)
