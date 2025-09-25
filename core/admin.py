from django.contrib import admin
from .models import Association, Role, Membre, Reglement, Match, Contribution, Depense, Sanction, Photo

admin.site.register(Association)
admin.site.register(Role)
admin.site.register(Membre)
admin.site.register(Reglement)
admin.site.register(Match)
admin.site.register(Contribution)
admin.site.register(Depense)
admin.site.register(Sanction)
admin.site.register(Photo)