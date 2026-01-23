from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

Utilisateur = get_user_model()


# ==================== SERIALIZERS PRINCIPAUX ====================

class ConnexionSerializer(serializers.Serializer):
    username = serializers.CharField()
    mot_de_passe = serializers.CharField(write_only=True)


class ProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les produits"""
    
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'quantite', 'camion', 'date_arrivee', 'date_sortie', 'statut']
    
    def validate(self, data):
        """Validation: si statut=sortie, date_sortie doit être renseignée"""
        if data.get('statut') == 'sortie' and not data.get('date_sortie'):
            raise serializers.ValidationError(
                "La date de sortie est obligatoire lorsque le statut est 'sortie'."
            )
        return data


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


class ItemNoteDeFraisSerializer(serializers.ModelSerializer):
    """Serializer pour les items de note de frais"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = ItemNoteDeFrais
        fields = ['id', 'type', 'type_display', 'montant', 'libelle']


class NoteDeFraisSerializer(serializers.ModelSerializer):
    """Serializer simple pour les notes de frais"""
    items = ItemNoteDeFraisSerializer(many=True, read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    montant_total = serializers.ReadOnlyField()

    
    class Meta:
        model = NoteDeFrais
        fields = ['id', 'reference', 'date_creation', 'tva', 'devise', 
                  'devise_display', 'montant_total', 'items', 'status', 'status_display']
        read_only_fields = ['reference', 'date_creation', 'montant_total']


class NoteDeFraisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création et modification de note de frais avec items"""
    items = ItemNoteDeFraisSerializer(many=True)

    class Meta:
        model = NoteDeFrais
        fields = ['tva', 'devise', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        from django.db import transaction
        with transaction.atomic():
            note = NoteDeFrais.objects.create(**validated_data)

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
            # Mise à jour des champs simples
            instance.tva = validated_data.get('tva', instance.tva)
            instance.devise = validated_data.get('devise', instance.devise)
            instance.save()

            # Mise à jour des items
            if items_data is not None:
                # stratégie simple et sûre :
                # on supprime puis on recrée
                instance.items.all().delete()

                for item_data in items_data:
                    ItemNoteDeFrais.objects.create(
                        note_de_frais=instance,
                        **item_data
                    )

        return instance


class ItemDevisSerializer(serializers.ModelSerializer):
    """Serializer pour les items de devis"""
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemDevis
        fields = ['id', 'libelle', 'prix_unitaire', 'quantite', 'montant_total']


class DevisSerializer(serializers.ModelSerializer):
    """Serializer simple pour les devis"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    items = ItemDevisSerializer(many=True, read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Devis
        fields = ['id', 'reference', 'client', 'client_nom', 'port_arrive', 
                  'vessel', 'voyage', 'eta', 'etd', 'bl', 'date_creation', 
                  'tva', 'devise', 'devise_display', 'montant_total', 'items']
        read_only_fields = ['reference', 'date_creation', 'montant_total']


class DevisDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les devis avec toutes les informations"""
    client = ClientSerializer(read_only=True)
    items = ItemDevisSerializer(many=True, read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Devis
        fields = ['id', 'reference', 'client', 'port_arrive', 'vessel', 
                  'voyage', 'eta', 'etd', 'bl', 'date_creation', 'tva', 
                  'devise', 'devise_display', 'montant_total', 'items']
        read_only_fields = ['reference', 'date_creation', 'montant_total']


class DevisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création et modification de devis avec items"""
    items = ItemDevisSerializer(many=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True
    )

    class Meta:
        model = Devis
        fields = [
            'client_id', 'port_arrive', 'vessel', 'voyage',
            'eta', 'etd', 'bl', 'tva', 'devise', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        from django.db import transaction
        with transaction.atomic():
            devis = Devis.objects.create(**validated_data)

            for item_data in items_data:
                ItemDevis.objects.create(
                    devis=devis,
                    **item_data
                )

        return devis

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
                    ItemDevis.objects.create(
                        devis=instance,
                        **item_data
                    )

        return instance


class ItemFactureSerializer(serializers.ModelSerializer):
    """Serializer pour les items de facture"""
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemFacture
        fields = ['id', 'libelle', 'prix_unitaire', 'quantite', 'montant_total']


class FactureSerializer(serializers.ModelSerializer):
    """Serializer simple pour les factures"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    items = ItemFactureSerializer(many=True, read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Facture
        fields = ['id', 'reference', 'client', 'client_nom', 'port_arrive', 
                  'vessel', 'voyage', 'eta', 'etd', 'bl', 'date_creation', 
                  'tva', 'devise', 'devise_display', 'montant_total', 'items']
        read_only_fields = ['reference', 'date_creation', 'montant_total']


class FactureDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les factures avec toutes les informations"""
    client = ClientSerializer(read_only=True)
    items = ItemFactureSerializer(many=True, read_only=True)
    devise_display = serializers.CharField(source='get_devise_display', read_only=True)
    montant_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Facture
        fields = ['id', 'reference', 'client', 'port_arrive', 'vessel', 
                  'voyage', 'eta', 'etd', 'bl', 'date_creation', 'tva', 
                  'devise', 'devise_display', 'montant_total', 'items']
        read_only_fields = ['reference', 'date_creation', 'montant_total']


class FactureCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création et modification de factures avec items"""
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
            'eta', 'etd', 'bl', 'tva', 'devise', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        from django.db import transaction
        with transaction.atomic():
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