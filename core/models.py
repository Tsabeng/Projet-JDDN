from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Association(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_creation = models.DateField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    cotisation_match = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)  # 500 FCFA par membre
    amende_retard = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # 100 FCFA pour retard
    heure_debut_match = models.TimeField(default='08:00:00')  # 8h

    def __str__(self):
        return self.nom

    @property
    def solde(self):
        # Calcul du solde : entrées (via matchs) - dépenses
        entrees = sum(
            c.montant for match in self.matches.all()
            for c in match.contributions.all()
        ) if self.matches.exists() else 0
        depenses = sum(d.montant for d in self.depenses.all()) if self.depenses.exists() else 0
        return entrees - depenses
class Role(models.Model):
    ROLE_CHOICES = [
        ('membre_simple', 'Membre Simple'),
        ('president', 'Président'),
        ('vice_president', 'Vice-Président'),
        ('censeur', 'Censeur'),
        ('secretaire', 'Secrétaire'),
        ('tresorier', 'Trésorier'),
        ('conseiller', 'Conseiller'),
        ('commissaire_comptes', 'Commissaire aux Comptes'),
        ('charge_communication', 'Chargé de la Communication'),
    ]
    nom = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_nom_display()



class Membre(AbstractUser):
    association = models.ForeignKey('Association', on_delete=models.CASCADE, related_name='membres', null=True)
    pseudo = models.CharField(max_length=50, unique=True)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='membres/', blank=True, null=True)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)

    # Ajouter related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='membre_groups',  # Nom unique pour éviter le conflit avec auth.User
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='membre_permissions',  # Nom unique pour éviter le conflit avec auth.User
        help_text=_('Specific permissions for this user.'),
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.pseudo})"

    def is_bureau(self):
        return self.role and self.role.nom != 'membre_simple'

class Reglement(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='reglements')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    amende = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.titre

class Match(models.Model):
    TYPE_CHOICES = [
        ('match_dimanche', 'Match du Dimanche'),
        ('contre', 'Contre (Affrontement)'),
    ]
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='matches')
    type_match = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_match = models.DateTimeField()
    lieu = models.CharField(max_length=100, blank=True)
    adversaire = models.CharField(max_length=100, blank=True)  # Pour les contres
    mise = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Somme exigée pour contres

    def __str__(self):
        return f"{self.titre} ({self.get_type_match_display()})"

class Contribution(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='contributions')
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Depense(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='depenses')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    approuve_par = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True)  # Typiquement trésorier

class Sanction(models.Model):
    TYPE_CHOICES = [
        ('amende', 'Amende'),
        ('suspension', 'Suspension'),
    ]
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    type_sanction = models.CharField(max_length=20, choices=TYPE_CHOICES)
    motif = models.TextField()
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)

class Photo(models.Model):
    titre = models.CharField(max_length=200)
    image = models.ImageField(upload_to='photos/')
    description = models.TextField(blank=True)
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)  # Associer à un match si pertinent
    association = models.ForeignKey(Association, on_delete=models.CASCADE)

class Annonce(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='annonces')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    publie_par = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titre