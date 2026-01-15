from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

Utilisateur = get_user_model()

class ConnexionSerializer(serializers.Serializer):
    telephone = serializers.CharField()
    mot_de_passe = serializers.CharField(write_only=True)


class BoiteArchiveSerializer(serializers.ModelSerializer):
    """Serializer simple pour les boîtes d'archive"""
    nombre_dossiers = serializers.SerializerMethodField()
    
    class Meta:
        model = BoiteArchive
        fields = ['id', 'reference', 'taille', 'date_creation', 'nombre_dossiers']
        read_only_fields = ['reference', 'date_creation']
    
    def get_nombre_dossiers(self, obj):
        """Retourne le nombre de dossiers dans la boîte"""
        return obj.dossiers.count()


class DossierSerializer(serializers.ModelSerializer):
    """Serializer simple du dossier"""
    path = serializers.ReadOnlyField()
    boite = BoiteArchiveSerializer(read_only=True, allow_null=True)  # MODIFIÉ: allow_null
    boite_id = serializers.PrimaryKeyRelatedField(
        queryset=BoiteArchive.objects.all(),
        source='boite',
        write_only=True,
        required=False,  # MODIFIÉ: pas obligatoire
        allow_null=True  # AJOUTÉ
    )
    
    date_creation = serializers.DateTimeField(
        format="%Y-%m-%d",
        read_only=True
    )
    
    class Meta:
        model = Dossier
        fields = ['id', 'numero', 'titre', 'type', 'date_creation', 'libelle', 'etape', 'path', 'boite', 'boite_id']


class DossierDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé du dossier avec ses pièces jointes"""
    pieces = serializers.SerializerMethodField()
    boite = BoiteArchiveSerializer(read_only=True, allow_null=True)  # MODIFIÉ: allow_null
    
    date_creation = serializers.DateTimeField(
        format="%Y-%m-%d",
        read_only=True
    )
    
    class Meta:
        model = Dossier
        fields = ['id', 'numero', 'titre', 'type', 'date_creation', 'libelle', 'etape', 'pieces', 'boite']
    
    def get_pieces(self, obj):
        pieces = obj.pieces.all()
        return PieceJointeSerializer(pieces, many=True).data


class PieceJointeSerializer(serializers.ModelSerializer):
    """Serializer simple de pièce jointe"""
    path = serializers.ReadOnlyField()
    
    class Meta:
        model = PieceJointe
        fields = ['id', 'titre', 'date_creation', 'fichier', 'path', 'dossier']


class PieceJointeDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé de pièce jointe avec détails du dossier"""
    dossier = DossierSerializer(read_only=True)
    path = serializers.ReadOnlyField()
    
    class Meta:
        model = PieceJointe
        fields = ['id', 'titre', 'date_creation', 'fichier', 'path', 'dossier']


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'


class UtilisateurCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }


class PieceJointeUploadSerializer(serializers.Serializer):
    fichiers = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )


class DossierCreateSerializer(serializers.ModelSerializer):
    fichiers = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )
    boite_id = serializers.PrimaryKeyRelatedField(
        queryset=BoiteArchive.objects.all(),
        source='boite',
        required=False,  # MODIFIÉ: pas obligatoire
        allow_null=True  # AJOUTÉ
    )
    
    class Meta:
        model = Dossier
        fields = ['titre', 'type', 'libelle', 'fichiers', 'boite_id']
    
    def create(self, validated_data):
        fichiers = validated_data.pop('fichiers')
        
        from django.db import transaction
        with transaction.atomic():
            dossier = Dossier.objects.create(**validated_data)
            
            for file in fichiers:
                PieceJointe.objects.create(
                    titre=file.name,
                    fichier=file,
                    dossier=dossier
                )
        
        return dossier


class BoiteArchiveDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les boîtes d'archive avec leurs dossiers"""
    dossiers = DossierSerializer(many=True, read_only=True)
    nombre_dossiers = serializers.SerializerMethodField()
    taux_remplissage = serializers.SerializerMethodField()
    
    class Meta:
        model = BoiteArchive
        fields = ['id', 'reference', 'taille', 'date_creation', 'nombre_dossiers', 'taux_remplissage', 'dossiers']
        read_only_fields = ['reference', 'date_creation']
    
    def get_nombre_dossiers(self, obj):
        return obj.dossiers.count()
    
    def get_taux_remplissage(self, obj):
        """Calcule le pourcentage de remplissage de la boîte"""
        nombre = obj.dossiers.count()
        if obj.taille > 0:
            return round((nombre / obj.taille) * 100, 2)
        return 0


# NOUVEAU: Serializer pour assigner une boîte à un dossier
class AssignerBoiteSerializer(serializers.Serializer):
    """Serializer pour assigner une boîte à un dossier"""
    boite_id = serializers.PrimaryKeyRelatedField(
        queryset=BoiteArchive.objects.all(),
        required=True
    )