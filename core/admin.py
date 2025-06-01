from django.contrib import admin
from .models import Artist, Album

admin.site.register(Artist)

admin.site.register(Album)

from django.contrib import admin

# Change the text shown at the top left of the admin
admin.site.site_header = "Painel de admin"

# Change the browser tab title
admin.site.site_title = "Admin"

# Change the title shown on the admin homepage
admin.site.index_title = "Bem vindo ao painel de controlo!"
