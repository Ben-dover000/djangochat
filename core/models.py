from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não dizer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

    @property
    def idade(self):
        import datetime
        if self.data_nascimento:
            today = datetime.date.today()
            born = self.data_nascimento
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None


class Artist(models.Model):
    id_artista = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(null=True, blank=True)
    data_nascimento = models.DateField()
    data_falecimento = models.DateField(null=True, blank=True)
    imagem = models.ImageField(upload_to='artistas/', null=True, blank=True)

    favorito = models.ManyToManyField(User, related_name='artista_favorito', blank=True)

    def __str__(self):
        return self.nome

class Album(models.Model):
    GENRE_CHOICES = [
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('classico', 'Clássica'),
        ('hip_hop', 'Hip Hop'),
        ('eletronica', 'Eletrônica'),
    ]

    id_album = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    breve_descricao = models.TextField(null=True, blank=True)
    descricao = models.TextField()
    genero = models.CharField(max_length=50, choices=GENRE_CHOICES)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_de_lancamento = models.DateField()
    imagem = models.ImageField(upload_to='albums/', null=True, blank=True)
    artista = models.ForeignKey(Artist, on_delete=models.CASCADE, default=1)
    favorito = models.ManyToManyField(User, related_name='album_favorito', blank=True)


    def __str__(self):
        return self.nome
    