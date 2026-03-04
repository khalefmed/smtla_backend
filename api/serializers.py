from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from django.db.models import Sum

Utilisateur = get_user_model()


# ==================== SERIALIZERS DE BASE ====================

class ConnexionSerializer(serializers.Serializer):
    username = serializers.CharField()
    mot_de_passe = serializers.CharField(write_only=True)


class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'prenom', 'nom', 'telephone', 'email', 
                  'type', 'type_display', 'password', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Utilisateur(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UtilisateurCustomSerializer(serializers.ModelSerializer):
    """Serializer personnalisé pour les utilisateurs avec tous les champs"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Utilisateur
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UtilisateurSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple pour afficher les informations basiques de l'utilisateur"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'prenom', 'nom', 'type', 'type_display']


# ==================== CLIENT & FOURNISSEUR ====================

class ClientSerializer(serializers.ModelSerializer):
    """Serializer pour les clients"""
    nombre_devis = serializers.SerializerMethodField()
    nombre_factures = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = ['id', 'nom', 'telephone', 'email', 'adresse', 'nif', 
                  'nombre_devis', 'nombre_factures']
    
    def get_nombre_devis(self, obj):
        return obj.devis.count()
    
    def get_nombre_factures(self, obj):
        return obj.factures.count()


class FournisseurSerializer(serializers.ModelSerializer):
    """Serializer pour les fournisseurs - Spec 9"""
    
    class Meta:
        model = Fournisseur
        fields = ['id', 'nom', 'nif', 'adresse', 'email', 'raison_sociale', 'telephone']


# ==================== TYPE MATERIEL ====================

class TypeMaterielSerializer(serializers.ModelSerializer):
    """Serializer pour les types de matériel - Spec 5"""
    
    class Meta:
        model = TypeMateriel
        fields = ['id', 'nom', 'description', 'date_creation']
        read_only_fields = ['date_creation']


# ==================== ROTATION ====================

class RotationSerializer(serializers.ModelSerializer):
    """Serializer pour les rotations (ancien Produit)"""
    type_produit_nom = serializers.CharField(source='type_produit.nom', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Rotation
        fields = ['id', 'type_produit', 'type_produit_nom', 'type', 'type_display',
                  'numero_bordereau', 'observation', 'quantite', 'camion', 
                  'date_rotation', 'date_creation']
        read_only_fields = ['date_creation']


class RotationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de rotations"""
    type_produit_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeMateriel.objects.all(),
        source='type_produit',
        write_only=True
    )
    
    class Meta:
        model = Rotation
        fields = ['type_produit_id', 'type', 'numero_bordereau', 'observation',
                  'quantite', 'camion', 'date_rotation']


# ==================== ROTATIONS ENTRANTES & SORTANTES ====================


class RotationEntranteSerializer(serializers.ModelSerializer):
    """Serializer pour les rotations entrantes - Spec 6"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    type_materiel_nom = serializers.CharField(source='type_materiel.nom', read_only=True)
    
    class Meta:
        model = RotationEntrante
        fields = ['id', 'client', 'client_nom', 'type_materiel', 'type_materiel_nom',
                  'numero_bordereau', 'observation', 'date_arrivee', 'camion', 'navire', 
                  'quantite', 'date_creation']
        read_only_fields = ['date_creation']


class RotationEntranteCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de rotations entrantes"""
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    type_materiel_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeMateriel.objects.all(),
        source='type_materiel',
        write_only=True
    )
    
    class Meta:
        model = RotationEntrante
        fields = ['client_id', 'type_materiel_id', 'numero_bordereau', 
                  'observation', 'date_arrivee', 'camion', 'quantite', 'navire',]


class RotationSortanteSerializer(serializers.ModelSerializer):
    """Serializer pour les rotations sortantes - Spec 7"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    type_materiel_nom = serializers.CharField(source='type_materiel.nom', read_only=True)
    
    class Meta:
        model = RotationSortante
        fields = ['id', 'client', 'client_nom', 'type_materiel', 'type_materiel_nom',
                  'numero_bordereau', 'observation', 'date_sortie', 'camion', 'navire',
                  'quantite', 'date_creation']
        read_only_fields = ['date_creation']


class RotationSortanteCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de rotations sortantes avec validation de stock"""
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    type_materiel_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeMateriel.objects.all(),
        source='type_materiel',
        write_only=True
    )
    
    class Meta:
        model = RotationSortante
        fields = ['client_id', 'type_materiel_id', 'numero_bordereau', 
                  'observation', 'date_sortie', 'camion', 'quantite', 'navire',]

    def validate(self, data):
        """
        Vérifie si la quantité sortante ne dépasse pas le stock disponible (Entrées - Sorties existantes)
        """
        client = data.get('client')
        type_materiel = data.get('type_materiel')
        quantite_sortie_voulue = data.get('quantite')

        # 1. Calculer le total des entrées pour ce client et ce matériel
        total_entrees = RotationEntrante.objects.filter(
            client=client,
            type_materiel=type_materiel
        ).aggregate(total=Sum('quantite'))['total'] or 0

        # 2. Calculer le total des sorties déjà effectuées
        total_sorties_existantes = RotationSortante.objects.filter(
            client=client,
            type_materiel=type_materiel
        ).aggregate(total=Sum('quantite'))['total'] or 0

        # 3. Calculer le stock disponible
        stock_disponible = total_entrees - total_sorties_existantes

        # 4. Validation
        if quantite_sortie_voulue > stock_disponible:
            raise serializers.ValidationError({
                "quantite": f"Stock insuffisant pour ce client. Disponible : {stock_disponible}, Demandé : {quantite_sortie_voulue}."
            })

        return data

# ==================== EXPRESSION DE BESOIN ====================

class ItemExpressionBesoinSerializer(serializers.ModelSerializer):
    """Serializer pour les items d'expression de besoin - Spec 1"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = ItemExpressionBesoin
        fields = ['id', 'type', 'type_display', 'montant', 'libelle']

class ExpressionBesoinSerializer(serializers.ModelSerializer):
    """Serializer complet pour la consultation des EB"""
    items = ItemExpressionBesoinSerializer(many=True, read_only=True)
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    # Ajout du type pour la gestion automatique des signatures PDF
    valideur_type = serializers.CharField(source='valideur.type', read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ExpressionBesoin
        fields = [
            'id', 'reference', 'nom_demandeur', 'direction', 'affectation',
            'bl_awb', 'navire', 'eta', 'status', 'status_display', 
            'date_creation', 'tva', 'devise', 'devise_display', 
            'montant_total', 'items', 'createur', 'createur_nom',
            'valideur', 'valideur_nom', 'valideur_type', 'date_validation'
        ]
        read_only_fields = ['reference', 'date_creation', 'montant_total', 
                            'createur', 'valideur', 'date_validation']


class ExpressionBesoinCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création et mise à jour d'EB"""
    items = ItemExpressionBesoinSerializer(many=True)
    
    class Meta:
        model = ExpressionBesoin
        fields = [
            'nom_demandeur', 'direction', 'affectation', 'bl_awb', 'navire', 'eta',
            'tva', 'devise', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        from django.db import transaction
        with transaction.atomic():
            # Récupération du créateur via le contexte de la requête
            validated_data['createur'] = self.context['request'].user
            expression = ExpressionBesoin.objects.create(**validated_data)
            
            for item_data in items_data:
                ItemExpressionBesoin.objects.create(
                    expression_besoin=expression,
                    **item_data
                )
        
        return expression
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        from django.db import transaction
        with transaction.atomic():
            # Mise à jour des champs (incluant nom_demandeur, direction, affectation)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Mise à jour synchronisée des items
            if items_data is not None:
                instance.items.all().delete()
                
                for item_data in items_data:
                    ItemExpressionBesoin.objects.create(
                        expression_besoin=instance,
                        **item_data
                    )
        
        return instance


# ==================== NOTE DE FRAIS ====================

class ItemNoteDeFraisSerializer(serializers.ModelSerializer):
    """Serializer pour les items de note de frais"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = ItemNoteDeFrais
        fields = ['id', 'type', 'type_display', 'montant', 'libelle']

class NoteDeFraisSerializer(serializers.ModelSerializer):
    """Serializer pour l'affichage des notes de frais - Spec 2 (Optimisé)"""
    items = ItemNoteDeFraisSerializer(many=True, read_only=True)
    
    # Informations récupérées de l'Expression de Besoin parente
    expression_besoin_reference = serializers.CharField(source='expression_besoin.reference', read_only=True)
    client_beneficiaire_nom = serializers.CharField(source='expression_besoin.client_beneficiaire.nom', read_only=True)
    bl_awb = serializers.CharField(source='expression_besoin.bl_awb', read_only=True)
    navire = serializers.CharField(source='expression_besoin.navire', read_only=True)
    eta = serializers.DateTimeField(source='expression_besoin.eta', read_only=True)
    tva = serializers.BooleanField(source='expression_besoin.tva', read_only=True)
    devise = serializers.CharField(source='expression_besoin.devise', read_only=True)
    devise_display = serializers.CharField(source='expression_besoin.get_devise_display', read_only=True)
    
    # Traçabilité et Statut
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = NoteDeFrais
        fields = [
            'id', 'reference', 'expression_besoin', 'expression_besoin_reference',
            'client_beneficiaire_nom', 'bl_awb', 'navire', 'eta', 'tva', 'devise', 
            'devise_display', 'montant_total', 'items', 'status', 'status_display', 
            'createur', 'createur_nom', 'valideur', 'valideur_nom', 'date_validation', 
            'date_creation'
        ]
        read_only_fields = ['reference', 'date_creation', 'montant_total']

class NoteFraisDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour la Note de Frais avec son EB source"""
    items = ItemNoteDeFraisSerializer(many=True, read_only=True)
    expression_besoin_detail = ExpressionBesoinSerializer(source='expression_besoin', read_only=True)
    
    # Traçabilité
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Propriétés calculées (mises à plat pour un accès facile au premier niveau)
    tva = serializers.BooleanField(read_only=True)
    devise = serializers.CharField(read_only=True)
    devise_display = serializers.CharField(source='expression_besoin.get_devise_display', read_only=True)

    class Meta:
        model = NoteDeFrais
        fields = [
            'id', 
            'reference', 
            'status', 
            'status_display',
            'date_creation',
            'montant_total',
            'tva',
            'devise',
            'devise_display',
            'createur_nom',
            'valideur_nom',
            'date_validation',
            'items',                    # Items de la Note de Frais
            'expression_besoin_detail'   # Détails de l'EB source (inclut ses propres items)
        ]


class NoteDeFraisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier une note de frais à partir d'une EB - Spec 2"""
    items = ItemNoteDeFraisSerializer(many=True)
    expression_besoin_id = serializers.PrimaryKeyRelatedField(
        queryset=ExpressionBesoin.objects.all(),
        source='expression_besoin',
        write_only=True,
        required=True # Obligatoire selon votre nouvelle logique
    )

    class Meta:
        model = NoteDeFrais
        # On ne garde que l'EB et les items
        fields = ['expression_besoin_id', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        from django.db import transaction
        with transaction.atomic():
            # Le créateur est récupéré du contexte de la requête
            validated_data['createur'] = self.context['request'].user
            note = NoteDeFrais.objects.create(**validated_data)

            # Création des items réels de la NF
            for item_data in items_data:
                ItemNoteDeFrais.objects.create(
                    note_de_frais=note,
                    **item_data
                )
        return note

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        from django.db import transaction
        with transaction.atomic():
            # On ne change généralement pas l'EB une fois la NF créée
            # On met à jour les items
            if items_data is not None:
                instance.items.all().delete()
                for item_data in items_data:
                    ItemNoteDeFrais.objects.create(
                        note_de_frais=instance,
                        **item_data
                    )
            instance.save()
        return instance

# ==================== DEVIS ====================

class ItemDevisSerializer(serializers.ModelSerializer):
    """Serializer pour les items de devis"""
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemDevis
        fields = ['id', 'libelle', 'prix_unitaire', 'quantite', 'montant_total']


class DevisSerializer(serializers.ModelSerializer):
    """Serializer simple pour les devis - Spec 4"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    items = ItemDevisSerializer(many=True, read_only=True)
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Devis
        fields = ['id', 'reference', 'client', 'client_nom', 'port_arrive', 
                  'vessel', 'voyage', 'eta', 'etd', 'bl', 'date_creation', 
                  'tva', 'devise', 'devise_display', 'montant_total', 'items',
                  'status', 'status_display', 'createur', 'createur_nom',
                  'valideur', 'valideur_nom', 'date_validation']
        read_only_fields = ['reference', 'date_creation', 'montant_total',
                            'createur', 'valideur', 'date_validation']


class DevisDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les devis avec toutes les informations"""
    client = ClientSerializer(read_only=True)
    items = ItemDevisSerializer(many=True, read_only=True)
    createur = UtilisateurSimpleSerializer(read_only=True)
    valideur = UtilisateurSimpleSerializer(read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Devis
        fields = ['id', 'reference', 'client', 'port_arrive', 'vessel', 
                  'voyage', 'eta', 'etd', 'bl', 'date_creation', 'tva', 
                  'devise', 'devise_display', 'montant_total', 'items',
                  'status', 'status_display', 'createur', 'valideur', 
                  'date_validation']
        read_only_fields = ['reference', 'date_creation', 'montant_total',
                            'createur', 'valideur', 'date_validation']


class DevisCreateSerializer(serializers.ModelSerializer):
    items = ItemDevisSerializer(many=True)
    # On définit client_id pour qu'il lise directement la clé 'client_id' du JSON
    client_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Devis
        fields = [
            'client_id', 'port_arrive', 'vessel', 'voyage', 'bl', 'eta', 'etd', 'tva', 'devise', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # On récupère l'ID envoyé par le modal
        client_id = validated_data.pop('client_id')
        
        from django.db import transaction
        with transaction.atomic():
            validated_data['createur'] = self.context['request'].user
            # On assigne manuellement l'ID au champ client_id du modèle
            devis = Devis.objects.create(client_id=client_id, **validated_data)

            for item_data in items_data:
                ItemDevis.objects.create(devis=devis, **item_data)
        return devis

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        # Gestion de la mise à jour du client
        if 'client_id' in validated_data:
            instance.client_id = validated_data.pop('client_id')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                ItemDevis.objects.create(devis=instance, **item_data)
        return instance


# ==================== FACTURE ====================

class ItemFactureSerializer(serializers.ModelSerializer):
    """Serializer pour les items de facture"""
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemFacture
        fields = ['id', 'libelle', 'prix_unitaire', 'quantite', 'montant_total']


class FactureSerializer(serializers.ModelSerializer):
    """Serializer simple pour les factures - Spec 3"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    items = ItemFactureSerializer(many=True, read_only=True)
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Facture
        fields = ['id', 'reference', 'client', 'client_nom', 'port_arrive', 
                  'vessel', 'voyage', 'eta', 'etd', 'bl', 'date_creation', 
                  'tva', 'devise', 'devise_display', 'montant_total', 'items',
                  'status', 'status_display', 'est_privee', 'createur', 
                  'createur_nom', 'valideur', 'valideur_nom', 'date_validation']
        read_only_fields = ['reference', 'date_creation', 'montant_total',
                            'createur', 'valideur', 'date_validation']


class FactureDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les factures avec toutes les informations"""
    client = ClientSerializer(read_only=True)
    items = ItemFactureSerializer(many=True, read_only=True)
    createur = UtilisateurSimpleSerializer(read_only=True)
    valideur = UtilisateurSimpleSerializer(read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Facture
        fields = ['id', 'reference', 'client', 'port_arrive', 'vessel', 
                  'voyage', 'eta', 'etd', 'bl', 'date_creation', 'tva', 
                  'devise', 'devise_display', 'montant_total', 'items',
                  'status', 'status_display', 'est_privee', 'createur',
                  'valideur', 'date_validation']
        read_only_fields = ['reference', 'date_creation', 'montant_total',
                            'createur', 'valideur', 'date_validation']


class FactureCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création et modification de factures avec items - Spec 3"""
    items = ItemFactureSerializer(many=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )

    class Meta:
        model = Facture
        fields = [
            'client_id', 'port_arrive', 'vessel', 'voyage',
            'eta', 'etd', 'bl', 'tva', 'devise', 'est_privee', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        from django.db import transaction
        with transaction.atomic():
            # Le créateur doit être passé via le context
            validated_data['createur'] = self.context['request'].user
            facture = Facture.objects.create(**validated_data)

            for item_data in items_data:
                ItemFacture.objects.create(
                    facture=facture,
                    **item_data
                )

        return facture

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        from django.db import transaction
        with transaction.atomic():
            # Champs simples
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Items
            if items_data is not None:
                instance.items.all().delete()

                for item_data in items_data:
                    ItemFacture.objects.create(
                        facture=instance,
                        **item_data
                    )

        return instance


# ==================== BON DE COMMANDE ====================

class ItemBonCommandeSerializer(serializers.ModelSerializer):
    """Serializer pour les items de bon de commande - Spec 10"""
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemBonCommande
        fields = ['id', 'libelle', 'prix_unitaire', 'quantite', 'montant_total']


class BonCommandeSerializer(serializers.ModelSerializer):
    """Serializer simple pour les bons de commande - Spec 10"""
    fournisseur_nom = serializers.CharField(source='fournisseur.nom', read_only=True)
    fournisseur_email = serializers.CharField(source='fournisseur.email', read_only=True)
    fournisseur_adresse = serializers.CharField(source='fournisseur.adresse', read_only=True)
    fournisseur_raison_sociale = serializers.CharField(source='fournisseur.raison_sociale', read_only=True)
    fournisseur_nif = serializers.CharField(source='fournisseur.nif', read_only=True)
    fournisseur_telephone = serializers.CharField(source='fournisseur.telephone', read_only=True)
    items = ItemBonCommandeSerializer(many=True, read_only=True)
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = BonCommande
        fields = ['id', 'reference', 'fournisseur', 'fournisseur_nom',  'fournisseur_adresse','fournisseur_email','fournisseur_nif','fournisseur_raison_sociale','fournisseur_telephone',
                  'objet_commande', 'date', 'tva', 'status', 'status_display',
                  'date_creation', 'montant_total', 'items', 'createur', 
                  'createur_nom', 'valideur', 'valideur_nom', 'date_validation']
        read_only_fields = ['reference', 'date_creation', 'montant_total',
                            'createur', 'valideur', 'date_validation']


class BonCommandeDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les bons de commande"""
    fournisseur = FournisseurSerializer(read_only=True)
    items = ItemBonCommandeSerializer(many=True, read_only=True)
    createur = UtilisateurSimpleSerializer(read_only=True)
    valideur = UtilisateurSimpleSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = BonCommande
        fields = ['id', 'reference', 'fournisseur', 'objet_commande', 'date',
                  'tva', 'status', 'status_display', 'date_creation', 
                  'montant_total', 'items', 'createur', 'valideur', 'date_validation']
        read_only_fields = ['reference', 'date_creation', 'montant_total',
                            'createur', 'valideur', 'date_validation']


class BonCommandeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de bons de commande - Spec 10"""
    items = ItemBonCommandeSerializer(many=True)
    fournisseur_id = serializers.PrimaryKeyRelatedField(
        queryset=Fournisseur.objects.all(),
        source='fournisseur',
        write_only=True
    )
    
    class Meta:
        model = BonCommande
        fields = ['fournisseur_id', 'objet_commande', 'date', 'tva', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        from django.db import transaction
        with transaction.atomic():
            # Le créateur doit être passé via le context
            validated_data['createur'] = self.context['request'].user
            bon_commande = BonCommande.objects.create(**validated_data)
            
            for item_data in items_data:
                ItemBonCommande.objects.create(
                    bon_commande=bon_commande,
                    **item_data
                )
        
        return bon_commande
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        from django.db import transaction
        with transaction.atomic():
            # Champs simples
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Items
            if items_data is not None:
                instance.items.all().delete()
                
                for item_data in items_data:
                    ItemBonCommande.objects.create(
                        bon_commande=instance,
                        **item_data
                    )
        
        return instance
    




# ==================== BON À DÉLIVRER (BAD) ====================

class ItemBADSerializer(serializers.ModelSerializer):
    valideur_nom = serializers.CharField(source='valideur.get_full_name', read_only=True)
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)

    class Meta:
        model = ItemBAD
        fields = [
            'id', 'bl', 'package_number', 'weight', 
            'valideur', 'valideur_nom', 'createur', 'createur_nom'
        ]
        read_only_fields = ['createur', 'valideur']


class BADSerializer(serializers.ModelSerializer):
    items = ItemBADSerializer(many=True, read_only=True)
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    
    # Changé 'facture_reference' en 'facture_ref' pour correspondre au Frontend
    facture_ref = serializers.CharField(source='facture.reference', read_only=True)
    
    # On s'assure que l'ID de la facture est aussi renvoyé
    facture = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = BAD
        fields = [
            'id', 'reference', 'client', 'client_nom', 'facture', 
            'facture_ref', 'navire', 'nombre_jours', 'date', 
            'date_expiration', 'nom_representant', 'items', 'date_creation'
        ]
        read_only_fields = ['date_creation', 'reference']

class BADCreateSerializer(serializers.ModelSerializer):
    items = ItemBADSerializer(many=True)
    # Pour l'écriture (POST/PUT)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )
    facture_id = serializers.PrimaryKeyRelatedField(
        queryset=Facture.objects.all(),
        source='facture', # Indique à Django de remplir le champ 'facture' du modèle
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Pour la lecture (GET) - Utilisé par React pour afficher "Ref: FAC-001"
    client_nom = serializers.ReadOnlyField(source='client.nom')
    facture_ref = serializers.ReadOnlyField(source='facture.reference')

    class Meta:
        model = BAD
        fields = [
            'id', 'client_id', 'client_nom', 'facture_id', 'facture_ref', 
            'reference', 'navire', 'nombre_jours', 'nom_representant', 'items'
        ]
        read_only_fields = ['reference']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user # Optionnel si vous traquez le créateur

        from django.db import transaction
        with transaction.atomic():
            # Ici, 'facture' est déjà dans validated_data grâce à source='facture'
            bad = BAD.objects.create(**validated_data)
            for item_data in items_data:
                ItemBAD.objects.create(bad=bad, **item_data)
        return bad

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        from django.db import transaction
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if items_data is not None:
                instance.items.all().delete()
                for item_data in items_data:
                    ItemBAD.objects.create(bad=instance, **item_data)
        return instance
    




# ==================== ARCHIVES DOCUMENTAIRES (GED) ====================

class DocumentArchiveSerializer(serializers.ModelSerializer):
    """Serializer pour l'affichage des documents archivés"""
    type_label = serializers.CharField(source='get_type_doc_display', read_only=True)
    cree_par_nom = serializers.CharField(source='cree_par.get_full_name', read_only=True)
    taille_fichier = serializers.SerializerMethodField()

    class Meta:
        model = DocumentArchive
        fields = [
            'id', 'titre', 'fichier', 'type_doc', 'type_label', 
            'description', 'date_upload', 'cree_par', 'cree_par_nom',
            'taille_fichier'
        ]
        read_only_fields = ['date_upload', 'cree_par']

    def get_taille_fichier(self, obj):
        try:
            return obj.fichier.size
        except:
            return 0


class DocumentArchiveCreateSerializer(serializers.ModelSerializer):
    """Serializer pour l'upload et la modification de documents"""
    
    class Meta:
        model = DocumentArchive
        fields = ['titre', 'fichier', 'type_doc', 'description']

    def create(self, validated_data):
        # Récupération automatique de l'utilisateur connecté via le contexte de la requête
        validated_data['cree_par'] = self.context['request'].user
        return super().create(validated_data)



