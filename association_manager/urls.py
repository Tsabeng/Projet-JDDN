from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('bureau/', views.bureau, name='bureau'),
    path('rencontres/', views.rencontres, name='rencontres'),
    path('contact/', views.contact, name='contact'),
    path('membres/', views.membres, name='membres'),
    path('membre/<int:membre_id>/', views.membre_detail, name='membre_detail'),
    path('gestion/', views.gestion, name='gestion'),
    path('creer_association/', views.creer_association, name='creer_association'),
    path('ajouter_membre/', views.ajouter_membre, name='ajouter_membre'),
    path('supprimer_membre/<int:membre_id>/', views.supprimer_membre, name='supprimer_membre'),
    path('ajouter_reglement/', views.ajouter_reglement, name='ajouter_reglement'),
    path('ajouter_match/', views.ajouter_match, name='ajouter_match'),
    path('ajouter_photo/', views.ajouter_photo, name='ajouter_photo'),
    path('ajouter_annonce/', views.ajouter_annonce, name='ajouter_annonce'),
    path('accounts/', include('django.contrib.auth.urls')),
   # path('login/', views.login_view, name='login'),  
    #path('logout/', views.logout_view, name='logout'),
    path('annonces/', views.annonces, name='annonces'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)