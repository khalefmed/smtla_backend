from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max
from datetime import datetime
from django.core.validators import MinValueValidator


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


class Fournisseur(models.Model):
    """Modèle pour la gestion des fournisseurs - Spec 9"""
    nom = models.CharField(max_length=255)
    nif = models.CharField(max_length=50, blank=True, null=True, verbose_name="NIF")
    adresse = models.TextField()
    email = models.EmailField()
    raison_sociale = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']
        verbose_name_plural = "Fournisseurs"


class TypeMateriel(models.Model):
    """Modèle pour les types de matériel - Spec 5"""
    nom = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Type de matériel"
        verbose_name_plural = "Types de matériel"
        ordering = ['nom']


class RotationEntrante(models.Model):
    """Modèle pour les rotations entrantes - Spec 6"""
    
    # Définition des choix de statut
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='rotations_entrantes'
    )
    type_materiel = models.ForeignKey(
        TypeMateriel,
        on_delete=models.PROTECT,
        related_name='rotations_entrantes'
    )
    numero_bordereau = models.CharField(max_length=100)
    observation = models.TextField(blank=True, null=True)
    date_arrivee = models.DateTimeField()
    camion = models.CharField(max_length=100)
    navire = models.CharField(max_length=100, default='MV-BRIALLANCE')
    quantite = models.IntegerField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='en_cours'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.numero_bordereau} - {self.client.nom} - {self.status}"
    
    class Meta:
        verbose_name = "Rotation entrante"
        verbose_name_plural = "Rotations entrantes"
        ordering = ['-date_arrivee']


class RotationSortante(models.Model):
    """Modèle pour les rotations sortantes - Spec 7"""
    
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='rotations_sortantes'
    )
    type_materiel = models.ForeignKey(
        TypeMateriel,
        on_delete=models.PROTECT,
        related_name='rotations_sortantes'
    )
    numero_bordereau = models.CharField(max_length=100)
    observation = models.TextField(blank=True, null=True)
    date_sortie = models.DateTimeField()
    camion = models.CharField(max_length=100)
    navire = models.CharField(max_length=100, default='MV-BRIALLANCE')
    quantite = models.IntegerField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='en_cours'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.numero_bordereau} - {self.client.nom} - {self.status}"
    
    class Meta:
        verbose_name = "Rotation sortante"
        verbose_name_plural = "Rotations sortantes"
        ordering = ['-date_sortie']


class ExpressionBesoin(models.Model):
    """Modèle pour les expressions de besoin - Spec 1"""
    DEVISES = [
        ('EUR', 'Euro'),
        ('DOLLAR', 'Dollar'),
        ('MRU', 'Ouguiya'),
        ('XOF', 'Franc CFA'),
    ]
    STATUS = [
        ('attente', 'En attente'),
        ('en_cours', 'En cours de traitement'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
    ]
    
    reference = models.CharField(max_length=15, unique=True, editable=False)
    
    # --- Nouveaux Champs Ajoutés ---
    nom_demandeur = models.CharField(
        max_length=255, 
        default="Moustapha Seydna Aly", 
        verbose_name="Nom du demandeur"
    )
    direction = models.CharField(
        max_length=100, 
        default="Operation", 
        verbose_name="Direction"
    )
    affectation = models.CharField(
        max_length=255, 
        default="Bureau siege", 
        verbose_name="Affectation"
    )
    # ------------------------------

    client_beneficiaire = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='expressions_besoin',
        verbose_name="Client / Bénéficiaire",
        null=True, blank=True
    )
    bl_awb = models.CharField(max_length=100, verbose_name="BL / AWB", null=True, blank=True)
    navire = models.CharField(max_length=255, verbose_name="Navire", null=True, blank=True)
    eta = models.DateTimeField(verbose_name="ETA (Estimated Time of Arrival)", null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS, default='attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    tva = models.BooleanField(default=False, verbose_name="TVA")
    devise = models.CharField(max_length=10, choices=DEVISES, default='MRU')
    
    # Traçabilité
    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='expressions_besoin_creees',
        null=True,
        blank=True
    )
    valideur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        related_name='expressions_besoin_validees',
        null=True,
        blank=True
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    def generer_reference(self):
        from datetime import datetime
        from django.db.models import Max
        
        annee = datetime.now().year
        dernier = ExpressionBesoin.objects.filter(
            reference__endswith=f"/{annee}"
        ).aggregate(max_num=Max('reference'))
        
        if dernier['max_num']:
            try:
                # Gestion sécurisée du split au cas où le format change
                last_counter = int(dernier['max_num'].split('/')[0].replace('EB', ''))
                compteur = last_counter + 1
            except (ValueError, IndexError):
                compteur = 1
        else:
            compteur = 1
        
        return f"EB{compteur:03d}/{annee}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.nom_demandeur}"
    
    @property
    def montant_total(self):
        from decimal import Decimal
        total = sum(
            (item.montant_total for item in self.items.all()),
            Decimal('0.00')
        )
        if self.tva:
            total *= Decimal('1.16')  # TVA 16%
        return total
    
    class Meta:
        verbose_name = "Expression de besoin"
        verbose_name_plural = "Expressions de besoin"
        ordering = ['-date_creation']


class ItemExpressionBesoin(models.Model):
    """Items pour les expressions de besoin - Spec 1"""
    TYPES = [
        ('nourriture', 'Nourriture'),
        ('hebergement', 'Hébergement'),
        ('medicament', 'Médicament'),
        ('carburant', 'Carburant'),
        ('entretien', 'Entretien'),
        ('telecom', 'Télécom'),
        ('avance_salaire', 'Avance sur salaire'),
        ('avance_paiement', 'Avance sur paiement'),
        ('equipement', 'Equipement'),
    ]
    
    expression_besoin = models.ForeignKey(
        ExpressionBesoin,
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
    """
    Modèle pour les notes de frais - Spec 2
    Désormais lié obligatoirement à une Expression de Besoin pour éviter la duplication.
    """
    STATUS = [
        ('attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    
    reference = models.CharField(max_length=15, unique=True, editable=False)
    
    # Le lien devient le pivot central (OneToOne ou ForeignKey)
    # On le met en CASCADE ou PROTECT selon votre flux métier
    expression_besoin = models.ForeignKey(
        ExpressionBesoin,
        on_delete=models.PROTECT, 
        related_name='notes_frais',
        verbose_name="Expression de besoin source",
        null=True, blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS, default='attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Traçabilité
    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='notes_frais_creees',
        null=True, blank=True
    )
    valideur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        related_name='notes_frais_validees',
        null=True, blank=True
    )
    date_validation = models.DateTimeField(null=True, blank=True)

    # --- Accès aux données de l'EB via propriétés pour simplifier le Serializer ---
    @property
    def client_beneficiaire(self):
        return self.expression_besoin.client_beneficiaire

    @property
    def devise(self):
        return self.expression_besoin.devise

    @property
    def tva(self):
        return self.expression_besoin.tva

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

    @property
    def montant_total(self):
        total = sum((item.montant_total for item in self.items.all()), Decimal('0.00'))
        # On récupère la règle de TVA de l'EB parente
        if self.expression_besoin.tva:
            total *= Decimal('1.16')
        return total

    class Meta:
        verbose_name = "Note de frais"
        verbose_name_plural = "Notes de frais"
        ordering = ['-date_creation']


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
        NoteDeFrais,
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


class Devis(models.Model):
    """Modèle pour les devis - Spec 4 (enrichi)"""
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
    
    reference = models.CharField(max_length=15, unique=True, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='devis'
    )
    port_arrive = models.CharField(max_length=255, verbose_name="Port d'arrivée", null=True, blank=True)
    vessel = models.CharField(max_length=255, null=True, blank=True)
    voyage = models.CharField(max_length=100, null=True, blank=True)
    eta = models.DateTimeField(verbose_name="ETA (Estimated Time of Arrival)", null=True, blank=True)
    etd = models.DateTimeField(verbose_name="ETD (Estimated Time of Departure)", null=True, blank=True)
    bl = models.CharField(max_length=100, verbose_name="Bill of Lading", null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    tva = models.BooleanField(default=False, verbose_name="TVA")
    devise = models.CharField(max_length=10, choices=DEVISES, default='MRU')
    status = models.CharField(max_length=20, choices=STATUS, default='attente')
    type = models.CharField(max_length=255, verbose_name="Type", null=True, blank=True)
    description = models.CharField(max_length=255, verbose_name="Description", null=True, blank=True)
    volume = models.CharField(max_length=255, verbose_name="Volume", null=True, blank=True)
    poids = models.CharField(max_length=255, verbose_name="Poids", null=True, blank=True)
    commentaire = models.TextField(verbose_name="Commentaire", null=True, blank=True)
    
    # Traçabilité - Spec 4
    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='devis_crees',
        null=True,
        blank=True
    )
    valideur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        related_name='devis_valides',
        null=True,
        blank=True
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
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


class Facture(models.Model):
    """Modèle pour les factures - Spec 3 (enrichie)"""
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
    
    reference = models.CharField(max_length=15, unique=True, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='factures'
    )
    port_arrive = models.CharField(max_length=255, verbose_name="Port d'arrivée", null=True, blank=True)
    vessel = models.CharField(max_length=255, null=True, blank=True)
    voyage = models.CharField(max_length=100, null=True, blank=True)
    eta = models.DateTimeField(verbose_name="ETA (Estimated Time of Arrival)", null=True, blank=True)
    etd = models.DateTimeField(verbose_name="ETD (Estimated Time of Departure)", null=True, blank=True)
    bl = models.CharField(max_length=100, verbose_name="Bill of Lading", null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    tva = models.BooleanField(default=False, verbose_name="TVA")
    devise = models.CharField(max_length=10, choices=DEVISES, default='MRU')
    status = models.CharField(max_length=20, choices=STATUS, default='attente')
    type = models.CharField(max_length=255, verbose_name="Type", null=True, blank=True)
    description = models.CharField(max_length=255, verbose_name="Description", null=True, blank=True)
    volume = models.CharField(max_length=255, verbose_name="Volume", null=True, blank=True)
    poids = models.CharField(max_length=255, verbose_name="Poids", null=True, blank=True)
    commentaire = models.TextField(verbose_name="Commentaire", null=True, blank=True)
    
    # Facture privée - Spec 3
    est_privee = models.BooleanField(default=False, verbose_name="Facture privée")
    
    # Traçabilité - Spec 3
    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='factures_creees',
        null=True,
        blank=True
    )
    valideur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        related_name='factures_validees',
        null=True,
        blank=True
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
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


class ItemFacture(models.Model):
    facture = models.ForeignKey(
        Facture,
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


class BonCommande(models.Model):
    """Modèle pour les bons de commande - Spec 10"""
    STATUS = [
        ('attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]
    
    reference = models.CharField(max_length=30, unique=True, editable=False)
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.PROTECT,
        related_name='bons_commande'
    )
    objet_commande = models.TextField(verbose_name="Objet de la commande")
    date = models.DateField()
    tva = models.BooleanField(default=False, verbose_name="TVA incluse")
    status = models.CharField(max_length=20, choices=STATUS, default='attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Traçabilité - Spec 10
    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='bons_commande_crees',
        null=True,
        blank=True
    )
    valideur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        related_name='bons_commande_valides',
        null=True,
        blank=True
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    def generer_reference(self):
        """Génère une référence au format SMTLA/BC/002/2026"""
        annee = datetime.now().year
        dernier = BonCommande.objects.filter(
            reference__endswith=f"/{annee}"
        ).aggregate(max_num=Max('reference'))
        
        if dernier['max_num']:
            # Extraire le numéro du format SMTLA/BC/XXX/YYYY
            parts = dernier['max_num'].split('/')
            last_counter = int(parts[2])
            compteur = last_counter + 1
        else:
            compteur = 1
        
        return f"SMTLA/BC/{compteur:03d}/{annee}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.fournisseur.nom}"
    
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
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ['-date_creation']


class ItemBonCommande(models.Model):
    """Items pour les bons de commande - Spec 10"""
    bon_commande = models.ForeignKey(
        BonCommande,
        on_delete=models.CASCADE,
        related_name='items'
    )
    libelle = models.CharField(max_length=255, verbose_name="Article")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    quantite = models.IntegerField()
    
    @property
    def montant_total(self):
        return self.prix_unitaire * self.quantite
    
    def __str__(self):
        return f"{self.libelle} - {self.quantite} x {self.prix_unitaire}"


class Rotation(models.Model):
    """Modèle pour les rotations (ancien Produit)"""
    TYPES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]
    
    type_produit = models.ForeignKey(
        TypeMateriel,
        on_delete=models.PROTECT,
        related_name='rotations',
        verbose_name="Type de produit"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPES,
        default='entree'
    )
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='rotations',
        verbose_name="Client concerné",
        null=True, blank=True
    )
    numero_bordereau = models.CharField(max_length=100)
    observation = models.TextField(blank=True, null=True)
    quantite = models.IntegerField()
    camion = models.CharField(max_length=100)
    date_rotation = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.numero_bordereau} - {self.type_produit.nom} - {self.get_type_display()}"
    
    class Meta:
        verbose_name_plural = "Rotations"
        ordering = ['-date_rotation']




class BAD(models.Model):
    """Modèle pour le Bon à Délivrer - Spec Logistique"""
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='bads')
    facture = models.ForeignKey(Facture, on_delete=models.SET_NULL, null=True, blank=True, related_name='bads')
    
    reference = models.IntegerField(unique=True, verbose_name="Référence BAD", blank=True)
    date = models.DateField(verbose_name="Date d'émission", null=True, blank=True)
    date_expiration = models.DateField(verbose_name="Date d'expiration", null=True, blank=True)
    
    # Nouveaux champs demandés
    navire = models.CharField(max_length=255, verbose_name="Navire", blank=True, null=True)
    nombre_jours = models.PositiveIntegerField(default=0, verbose_name="Nombre de jours")
    
    nom_representant = models.CharField(max_length=255, verbose_name="Nom du représentant")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BAD {self.reference} - {self.client.nom}"

    

    def save(self, *args, **kwargs):
        if not self.id and not self.reference:
            # Récupère la valeur max actuelle de 'reference'
            last_ref = BAD.objects.aggregate(Max('reference'))['reference__max']
            if last_ref is not None:
                self.reference = last_ref + 1
            else:
                self.reference = 101  # On commence à 101 (ou 1 selon votre choix)
        
        super(BAD, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Bon à Délivrer"
        verbose_name_plural = "Bons à Délivrer"
        ordering = ['-date_creation']


class ItemBAD(models.Model):
    """Items contenus dans un Bon à Délivrer"""
    bad = models.ForeignKey(BAD, on_delete=models.CASCADE, related_name='items')
    bl = models.CharField(max_length=100, verbose_name="BL")
    package_number = models.CharField(max_length=100, verbose_name="Nombre de colis")
    weight = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Poids")
    
    # Traçabilité
    valideur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, related_name='bad_items_valides', null=True, blank=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, related_name='bad_items_crees', null=True, blank=True)

    def __str__(self):
        return f"Item BL {self.bl} - BAD {self.bad.reference}"

    class Meta:
        verbose_name = "Item de BAD"
        verbose_name_plural = "Items de BAD"

    


class DocumentArchive(models.Model):
    """Modèle pour l'archivage documentaire - GED"""
    TYPES_DOCS = [
        ('BL', 'BL-CONNAISSEMENT'),
        ('MANIFESTE', 'MANIFESTE'),
        ('IMAGE', 'IMAGE'),
    ]

    titre = models.CharField(max_length=255)
    fichier = models.FileField(
        upload_to='archives/%Y/%m/',
        verbose_name="Fichier joint"
    )
    type_doc = models.CharField(
        max_length=20, 
        choices=TYPES_DOCS,
        verbose_name="Type de document"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Description / Note"
    )
    date_upload = models.DateTimeField(auto_now_add=True)
    
    # Traçabilité cohérente avec vos autres modèles
    cree_par = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        related_name='documents_archives', 
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.titre} ({self.get_type_doc_display()})"

    class Meta:
        verbose_name = "Document archivé"
        verbose_name_plural = "Archives Documentaires"
        ordering = ['-date_upload']
    




class PDA(models.Model):
    CURRENCY_CHOICES = [('EUR', 'Euro'), ('USD', 'Dollar')]
    
    # En-tête
    pda_number = models.CharField(max_length=50, unique=True, verbose_name="PDA N°")
    date = models.DateField(auto_now_add=True)
    client = models.ForeignKey(
        'Client', 
        on_delete=models.CASCADE, 
        related_name='pdas',
        verbose_name="Client / Principal",
        null=True, blank=True
    )

    createur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='pda_creees',
        null=True,
        blank=True
    )

    vessel_name = models.CharField(max_length=255)
    port_of_arrival = models.CharField(max_length=255, default="NOUAKCHOTT")
    cargo_description = models.TextField(blank=True)
    
    # Paramètres globaux
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    number_of_days = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    apply_vat = models.BooleanField(default=True, verbose_name="Appliquer TVA (16%)")
    
    # Remarques dynamiques
    remarks = models.TextField(blank=True, help_text="Texte libre pour les remarques en bas de page")

    def __str__(self):
        return f"PDA {self.pda_number} - {self.vessel_name}"

class PDAItem(models.Model):
    CATEGORY_CHOICES = [
        ('PORT_DUES', 'Ports Dues'),
        ('OTHER_EXPENSES', 'Other Expenses (Port Call Tax, etc.)'),
        ('STEVEDORING', 'Stevedoring/Handling on Board'),
    ]

    pda = models.ForeignKey(PDA, related_name='items', on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    label = models.CharField(max_length=255) # Ex: "PILOTAGE IN & OUT"
    
    # Champs pour le calcul
    grt_value = models.FloatField(default=0, help_text="Valeur GRT / Quantité / Tons")
    rate = models.FloatField(default=0)
    
    # Pour les Port Dues, le calcul est souvent (GRT * Rate)
    # Pour le Stevedoring, c'est (Tons * Rate)
    # On stocke le total_item pour faciliter l'affichage
    total_amount = models.FloatField(editable=False)

    def save(self, *args, **kwargs):
        # Logique de calcul simple par défaut
        self.total_amount = self.grt_value * self.rate
        super().save(*args, **kwargs)


