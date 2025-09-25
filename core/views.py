from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReglementForm
from .models import *
from .forms import *
from .forms import PhotoForm
from .models import Photo
from .models import Association, Contribution, Depense, Match, Membre
from .forms import DepenseForm
import logging


@login_required
def gestion(request):
    if not request.user.is_bureau():
        return render(request, 'core/403.html', status=403)
    association = request.user.association
    if not association:
        return render(request, 'core/403.html', {'error': 'Aucune association associée à cet utilisateur.'}, status=403)
    solde = association.solde
    contributions = Contribution.objects.filter(match__association=association)
    depenses = Depense.objects.filter(association=association)
    matches = Match.objects.filter(association=association)
    membres = Membre.objects.filter(association=association)
    depense_form = DepenseForm()

    if request.method == 'POST':
        if 'ajouter_contribution' in request.POST:
            match_id = request.POST.get('match_id')
            membre_ids = request.POST.getlist('membres')
            for membre_id in membre_ids:
                Contribution.objects.create(
                    match_id=match_id,
                    membre_id=membre_id,
                    montant=association.cotisation_match
                )
            messages.success(request, 'Contributions ajoutées avec succès.')
            return redirect('gestion')
        elif 'ajouter_depense' in request.POST:
            form = DepenseForm(request.POST)
            if form.is_valid():
                depense = form.save(commit=False)
                depense.association = association
                depense.approuve_par = request.user
                depense.save()
                messages.success(request, 'Dépense ajoutée avec succès.')
                return redirect('gestion')
            else:
                messages.error(request, 'Erreur dans le formulaire de dépense.')

    return render(request, 'core/gestion.html', {
        'association': association,
        'solde': solde,
        'contributions': contributions,
        'depenses': depenses,
        'matches': matches,
        'membres': membres,
        'depense_form': depense_form,
    })

@login_required
def ajouter_membre(request):
    if not request.user.is_bureau() or request.user.role.nom not in ['president', 'vice_president']:
        return render(request, 'core/403.html', status=403)
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES)
        if form.is_valid():
            membre = form.save(commit=False)
            membre.association = request.user.association
            membre.save()
            messages.success(request, 'Membre ajouté avec succès.')
            return redirect('gestion')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = MembreForm()
    return render(request, 'core/ajouter_membre.html', {'form': form})

@login_required
def ajouter_match(request):
    if not request.user.is_bureau():
        return render(request, 'core/403.html', status=403)
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.association = request.user.association
            match.save()
            messages.success(request, 'Match ajouté avec succès.')
            return redirect('gestion')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = MatchForm()
    return render(request, 'core/ajouter_match.html', {'form': form})

@login_required
def ajouter_photo(request):
    if not request.user.is_bureau():
        return render(request, 'core/403.html', status=403)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.association = request.user.association
            photo.save()
            messages.success(request, 'Photo ajoutée avec succès.')
            return redirect('gestion')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = PhotoForm()
    return render(request, 'core/ajouter_photo.html', {'form': form})

@login_required
def ajouter_annonce(request):
    if not request.user.is_bureau():
        return render(request, 'core/403.html', status=403)
    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        if form.is_valid():
            annonce = form.save(commit=False)
            annonce.association = request.user.association
            annonce.publie_par = request.user
            annonce.save()
            messages.success(request, 'Annonce ajoutée avec succès.')
            return redirect('gestion')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = AnnonceForm()
    return render(request, 'core/ajouter_annonce.html', {'form': form})

@login_required
def ajouter_reglement(request):
    if request.user.role.nom != 'censeur':
        return render(request, 'core/403.html', status=403)
    if request.method == 'POST':
        form = ReglementForm(request.POST)
        if form.is_valid():
            reglement = form.save(commit=False)
            reglement.association = request.user.association
            reglement.save()
            messages.success(request, 'Règlement ajouté avec succès.')
            return redirect('gestion')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = ReglementForm()
    return render(request, 'core/ajouter_reglement.html', {'form': form})


def home(request):
    association = Association.objects.first()  # Assume une seule association
    photos = Photo.objects.filter(association=association)[:5]  # Pour carousel
    return render(request, 'home.html', {'association': association, 'photos': photos})

def about(request):
    association = Association.objects.first()
    return render(request, 'about.html', {'association': association})

logger = logging.getLogger(__name__)

@login_required
def bureau(request):
    association = request.user.association
    if not association:
        logger.error("No association for user %s", request.user)
        return render(request, 'core/403.html', {'error': 'Aucune association associée à cet utilisateur.'}, status=403)
    bureau_membres = Membre.objects.filter(association=association, role__nom__in=['president', 'secretaire', 'tresorier']).order_by('role__nom')
    logger.debug("Found %d bureau members for association %s", bureau_membres.count(), association)
    bureau_membres_with_delays = [(membre, index / 3.0) for index, membre in enumerate(bureau_membres)]
    return render(request, 'core/bureau.html', {
        'association': association,
        'bureau_membres_with_delays': bureau_membres_with_delays,
    })

def rencontres(request):
    association = Association.objects.first()
    matches = Match.objects.filter(association=association).order_by('-date_match')
    return render(request, 'rencontres.html', {'matches': matches})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # TODO: Envoyer email ou sauvegarder
            messages.success(request, 'Message envoyé !')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def membres(request):
    association = Association.objects.first()
    membres = Membre.objects.filter(association=association)
    return render(request, 'membres.html', {'membres': membres})







@login_required
def creer_association(request):
    if Association.objects.exists():
        return redirect('home')  # Une seule association
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES)
        if form.is_valid():
            association = form.save()
            # Créez le président initial (le superuser)
            request.user.association = association
            request.user.role = Role.objects.get(nom='president')
            request.user.save()
            messages.success(request, 'Association créée !')
            return redirect('home')
    else:
        form = AssociationForm()
    return render(request, 'creer_association.html', {'form': form})


@login_required
def supprimer_membre(request, membre_id):
    if request.user.role.nom not in ['president', 'vice_president']:
        messages.error(request, "Seul le président ou vice-président peut supprimer un membre.")
        return redirect('membres')
    membre = get_object_or_404(Membre, id=membre_id, association=request.user.association)
    membre.delete()
    messages.success(request, 'Membre supprimé.')
    return redirect('membres')

@login_required
def annonces(request):
    association = request.user.association
    if not association:
        return render(request, 'core/403.html', {'error': 'Aucune association associée à cet utilisateur.'}, status=403)
    annonces = Annonce.objects.filter(association=association).order_by('-date_creation')
    # Ajouter un délai d'animation à chaque annonce
    annonces_with_delays = [(annonce, index / 3.0) for index, annonce in enumerate(annonces)]
    return render(request, 'core/annonces.html', {
        'association': association,
        'annonces_with_delays': annonces_with_delays,
    })