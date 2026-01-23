from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max
from datetime import datetime


class Produit(models.Model):
    STATUTS = [
        ('arrive', 'Arrivé'),
        ('sortie', 'Sorti'),
    ]
    
    nom = models.CharField(max_length=255)
    quantite = models.IntegerField()
    camion = models.CharField(max_length=100)
    date_arrivee = models.DateTimeField()
    date_sortie = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='arrive'
    )
    
    def __str__(self):
        return f"{self.nom} - {self.camion}"
    
    class Meta:
        verbose_name_plural = "Produits"


class Client(models.Model):
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    adresse = models.TextField()
    nif = models.CharField(max_length=50, unique=True, verbose_name="NIF")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']


class ItemNoteDeFrais(models.Model):
    TYPES = [
        ('nourriture', 'Nourriture'),
        ('hebergement', 'Hébergement'),
        ('medicament', 'Médicament'),
        ('carburant', 'Carburant'),
        ('entretien', 'Entretien'),
        ('telecom', 'Télécom'),
        ('avance', 'Avance'),
        ('divers', 'Divers'),
    ]
    
    note_de_frais = models.ForeignKey(
        'NoteDeFrais',
        on_delete=models.CASCADE,
        related_name='items'
    )
    libelle = models.CharField(max_length=255, default='Essence')
    type = models.CharField(max_length=20, choices=TYPES)
    montant = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def montant_total(self):
        return self.montant or Decimal('0.00')
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.montant}"


class NoteDeFrais(models.Model):
    DEVISES = [
        ('EUR', 'Euro'),
        ('DOLLAR', 'Dollar'),
        ('MRU', 'Ouguiya'),
        ('XOF', 'Franc CFA'),
    ]
    STATUS = [
        ('attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default='attente')
    reference = models.CharField(max_length=15, unique=True, editable=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    tva = models.BooleanField(default=False, verbose_name="TVA")
    devise = models.CharField(max_length=10, choices=DEVISES, default='MRU')
    
    def generer_reference(self):
        annee = datetime.now().year
        dernier = NoteDeFrais.objects.filter(
            reference__endswith=f"/{annee}"
        ).aggregate(max_num=Max('reference'))
        
        if dernier['max_num']:
            last_counter = int(dernier['max_num'].split('/')[0].replace('NF', ''))
            compteur = last_counter + 1
        else:
            compteur = 1
        
        return f"NF{compteur:03d}/{annee}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.reference
 
    @property
    def montant_total(self):
        total = sum(
            (item.montant_total for item in self.items.all()),
            Decimal('0.00')
        )
        if self.tva:
            total *= Decimal('1.16')  # TVA 16%
        return total
    
    class Meta:
        verbose_name = "Note de frais"
        verbose_name_plural = "Notes de frais"
        ordering = ['-date_creation']


class ItemDevis(models.Model):
    devis = models.ForeignKey(
        'Devis',
        on_delete=models.CASCADE,
        related_name='items'
    )
    libelle = models.CharField(max_length=255)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    quantite = models.IntegerField()
    
    @property
    def montant_total(self):
        return self.prix_unitaire * self.quantite
    
    def __str__(self):
        return f"{self.libelle} - {self.quantite} x {self.prix_unitaire}"


class Devis(models.Model):
    DEVISES = [
        ('EUR', 'Euro'),
        ('DOLLAR', 'Dollar'),
        ('MRU', 'Ouguiya'),
        ('XOF', 'Franc CFA'),
    ]
    
    reference = models.CharField(max_length=15, unique=True, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='devis'
    )
    port_arrive = models.CharField(max_length=255, verbose_name="Port d'arrivée")
    vessel = models.CharField(max_length=255)
    voyage = models.CharField(max_length=100)
    eta = models.DateTimeField(verbose_name="ETA (Estimated Time of Arrival)")
    etd = models.DateTimeField(verbose_name="ETD (Estimated Time of Departure)")
    bl = models.CharField(max_length=100, verbose_name="Bill of Lading")
    date_creation = models.DateTimeField(auto_now_add=True)
    tva = models.BooleanField(default=False, verbose_name="TVA")
    devise = models.CharField(max_length=10, choices=DEVISES, default='MRU')
    
    def generer_reference(self):
        annee = datetime.now().year
        dernier = Devis.objects.filter(
            reference__endswith=f"/{annee}"
        ).aggregate(max_num=Max('reference'))
        
        if dernier['max_num']:
            last_counter = int(dernier['max_num'].split('/')[0].replace('DV', ''))
            compteur = last_counter + 1
        else:
            compteur = 1
        
        return f"DV{compteur:03d}/{annee}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.client.nom}"
    
    @property
    def montant_total(self):
        total = sum(
            (item.montant_total for item in self.items.all()),
            Decimal('0.00')
        )
        if self.tva:
            total *= Decimal('1.16')  # TVA 16%
        return total
    
    class Meta:
        verbose_name_plural = "Devis"
        ordering = ['-date_creation']


class ItemFacture(models.Model):
    facture = models.ForeignKey(
        'Facture',
        on_delete=models.CASCADE,
        related_name='items'
    )
    libelle = models.CharField(max_length=255)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    quantite = models.IntegerField()
    
    @property
    def montant_total(self):
        return self.prix_unitaire * self.quantite
    
    def __str__(self):
        return f"{self.libelle} - {self.quantite} x {self.prix_unitaire}"


class Facture(models.Model):
    DEVISES = [
        ('EUR', 'Euro'),
        ('DOLLAR', 'Dollar'),
        ('MRU', 'Ouguiya'),
        ('XOF', 'Franc CFA'),
    ]
    
    reference = models.CharField(max_length=15, unique=True, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='factures'
    )
    port_arrive = models.CharField(max_length=255, verbose_name="Port d'arrivée")
    vessel = models.CharField(max_length=255)
    voyage = models.CharField(max_length=100)
    eta = models.DateTimeField(verbose_name="ETA (Estimated Time of Arrival)")
    etd = models.DateTimeField(verbose_name="ETD (Estimated Time of Departure)")
    bl = models.CharField(max_length=100, verbose_name="Bill of Lading")
    date_creation = models.DateTimeField(auto_now_add=True)
    tva = models.BooleanField(default=False, verbose_name="TVA")
    devise = models.CharField(max_length=10, choices=DEVISES, default='MRU')
    
    def generer_reference(self):
        annee = datetime.now().year
        dernier = Facture.objects.filter(
            reference__endswith=f"/{annee}"
        ).aggregate(max_num=Max('reference'))
        
        if dernier['max_num']:
            last_counter = int(dernier['max_num'].split('/')[0].replace('FA', ''))
            compteur = last_counter + 1
        else:
            compteur = 1
        
        return f"FA{compteur:03d}/{annee}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.client.nom}"
    
    @property
    def montant_total(self):
        total = sum(
            (item.montant_total for item in self.items.all()),
            Decimal('0.00')
        )
        if self.tva:
            total *= Decimal('1.16')  # TVA 16%
        return total
    
    class Meta:
        ordering = ['-date_creation']


class Utilisateur(AbstractUser):
    TYPES = [
        ('assistant', 'Assistant'),
        ('agent_port', 'Agent Port'),
        ('comptable', 'Comptable'),
        ('directeur_operations', 'Directeur des Opérations'),
        ('directeur_general', 'Directeur Général'),
    ]
    
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=30, choices=TYPES)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['telephone', 'prenom', 'nom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_type_display()})"
    
    class Meta:
        verbose_name_plural = "Utilisateurs"