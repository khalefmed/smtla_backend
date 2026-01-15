from datetime import timedelta
from rest_framework import generics
import csv, io

from api.permissions import *
from .models import *
from .serializers import *

from django.db import transaction as db_transaction

from django.db.models.functions import TruncMonth

import pandas as pd

from rest_framework.decorators import api_view, permission_classes
from django.utils.crypto import get_random_string

from django.http import HttpRequest
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from rest_framework.pagination import PageNumberPagination

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from django.db.models import Q, Avg, Sum, Count
from django.core.files.storage import default_storage
from django.db.models import Sum, Count, Q, FloatField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
import calendar



class DossierParEtapeView(generics.ListAPIView):
    serializer_class = DossierDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        etape = self.request.query_params.get('etape')

        print(etape)

        # 1️⃣ Filtre direct car etape toujours envoyée
        queryset = Dossier.objects.filter(etape=etape)

        # 2️⃣ Ordre décroissant par date
        return queryset.order_by('-date_creation')



class DossierListCreateView(generics.ListCreateAPIView):

    queryset = Dossier.objects.all().order_by('-date_creation')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DossierCreateSerializer
        return DossierSerializer
    


class DossierRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Dossier.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DossierDetailSerializer
        return DossierSerializer



class DossierEtapeUpdateView(generics.UpdateAPIView):

    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer

    def update(self, request, *args, **kwargs):
        dossier = self.get_object()
        nouvelle = request.data.get('etape')

        if nouvelle not in dict(Dossier.ETAPES):
            return Response(
                {"detail": "Étape invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        dossier.etape = nouvelle
        dossier.save()

        return Response(DossierSerializer(dossier).data)


# ==================== NOUVELLES VUES POUR BOITEARCHIVE ====================

class BoiteArchiveListCreateView(generics.ListCreateAPIView):
    """Liste toutes les boîtes ou crée une nouvelle boîte"""
    queryset = BoiteArchive.objects.all().order_by('-date_creation')
    serializer_class = BoiteArchiveSerializer
    permission_classes = [IsAuthenticated]


class BoiteArchiveRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime une boîte spécifique"""
    queryset = BoiteArchive.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoiteArchiveDetailSerializer
        return BoiteArchiveSerializer


class BoiteArchiveDisponiblesView(generics.ListAPIView):
    """Liste les boîtes qui ne sont pas pleines"""
    serializer_class = BoiteArchiveSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Retourne les boîtes où le nombre de dossiers < taille
        from django.db.models import Count, F
        return BoiteArchive.objects.annotate(
            nb_dossiers=Count('dossiers')
        ).filter(
            nb_dossiers__lt=F('taille')
        ).order_by('reference')


class AssignerBoiteView(APIView):
    """Assigne une boîte à un ou plusieurs dossiers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        boite_id = request.data.get('boite_id')
        dossier_ids = request.data.get('dossier_ids', [])
        
        if not boite_id:
            return Response(
                {"detail": "L'ID de la boîte est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not dossier_ids or not isinstance(dossier_ids, list):
            return Response(
                {"detail": "La liste des IDs de dossiers est requise"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            boite = BoiteArchive.objects.get(id=boite_id)
        except BoiteArchive.DoesNotExist:
            return Response(
                {"detail": "Boîte introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier la capacité de la boîte
        nb_dossiers_actuels = boite.dossiers.count()
        nb_nouveaux = len(dossier_ids)
        
        if nb_dossiers_actuels + nb_nouveaux > boite.taille:
            return Response(
                {
                    "detail": f"Capacité insuffisante. La boîte peut contenir {boite.taille} dossiers, "
                              f"elle en contient déjà {nb_dossiers_actuels}."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assigner la boîte aux dossiers
        dossiers = Dossier.objects.filter(id__in=dossier_ids)
        
        if not dossiers.exists():
            return Response(
                {"detail": "Aucun dossier trouvé avec ces IDs"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        dossiers.update(boite=boite)
        
        return Response(
            {
                "message": f"{dossiers.count()} dossier(s) assigné(s) à la boîte {boite.reference}",
                "boite": BoiteArchiveSerializer(boite).data
            },
            status=status.HTTP_200_OK
        )


class RetirerBoiteView(APIView):
    """Retire un ou plusieurs dossiers d'une boîte"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        dossier_ids = request.data.get('dossier_ids', [])
        
        if not dossier_ids or not isinstance(dossier_ids, list):
            return Response(
                {"detail": "La liste des IDs de dossiers est requise"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dossiers = Dossier.objects.filter(id__in=dossier_ids)
        
        if not dossiers.exists():
            return Response(
                {"detail": "Aucun dossier trouvé avec ces IDs"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        dossiers.update(boite=None)
        
        return Response(
            {"message": f"{dossiers.count()} dossier(s) retiré(s) de leur boîte"},
            status=status.HTTP_200_OK
        )




class ObtenirOuCreerBoiteView(APIView):
    """Obtient une boîte disponible ou en crée une nouvelle si toutes sont pleines"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from django.db.models import Count, F
        
        try:
            # 1. Chercher une boîte disponible (non pleine)
            boite_disponible = BoiteArchive.objects.annotate(
                nb_dossiers=Count('dossiers')
            ).filter(
                nb_dossiers__lt=F('taille')
            ).order_by('reference').first()
            
            # 2. Si une boîte est disponible, la retourner
            if boite_disponible:
                serializer = BoiteArchiveSerializer(boite_disponible)
                return Response({
                    'id': boite_disponible.id,
                    'reference': boite_disponible.reference,
                    'taille': boite_disponible.taille,
                    'nombre_dossiers': boite_disponible.dossiers.count(),
                    'message': f'Boîte {boite_disponible.reference} disponible'
                }, status=status.HTTP_200_OK)
            
            # 3. Sinon, créer une nouvelle boîte
            nouvelle_boite = BoiteArchive.objects.create()
            
            return Response({
                'id': nouvelle_boite.id,
                'reference': nouvelle_boite.reference,
                'taille': nouvelle_boite.taille,
                'nombre_dossiers': 0,
                'message': f'Nouvelle boîte {nouvelle_boite.reference} créée'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'detail': f'Erreur lors de l\'obtention/création de la boîte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

        
# ==================== FIN NOUVELLES VUES BOITEARCHIVE ====================


class PieceJointeListCreateView(generics.ListCreateAPIView):

    queryset = PieceJointe.objects.all().order_by('-date_creation')
    serializer_class = PieceJointeSerializer



class PieceJointeRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    queryset = PieceJointe.objects.all()
    serializer_class = PieceJointeSerializer



class UtilisateurListCreateView(generics.ListCreateAPIView):

    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer


class UtilisateurRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurCustomSerializer


class SeConnecter(TokenObtainPairView):
    serializer_class = ConnexionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telephone = serializer.validated_data['telephone']
        mot_de_passe = serializer.validated_data['mot_de_passe']

        utilisateur = Utilisateur.objects.filter(telephone=telephone).first()

        if utilisateur:

            utilisateur = authenticate(request, telephone=telephone, password=mot_de_passe)
            if utilisateur :
                
                refresh = RefreshToken.for_user(utilisateur)
                
                utilisateur = UtilisateurSerializer(utilisateur).data
                data = {
                    'token': str(refresh.access_token),
                    'utilisateur' : utilisateur,
                }
                
                return Response(data, status=status.HTTP_200_OK)
            
            else :
                return Response( status=401)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Utilisateur_profil(request):
    Utilisateur = request.user
    try:
        Utilisateur = UtilisateurSerializer(Utilisateur)
        return JsonResponse(Utilisateur.data)
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": f"Failed to load Utilisateurs profile {e}"
        })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_informations(request):
    user = request.user
    serializer = UtilisateurSerializer(user, data=request.data, partial=True)

    if serializer.is_valid() :
        serializer.save()
        return Response(serializer.data)
    return Response({"bad request"})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_mot_de_passe(request):
    Utilisateur = request.user
    try:
        data = json.loads(request.body.decode('utf-8'))
        ancien = data.get('ancien', {})
        nouveau = data.get('nouveau', {})

        if check_password(ancien, Utilisateur.password):
            Utilisateur.password = make_password(nouveau)
            Utilisateur.save()

            return Response({"message" : "Mot de passe modifié avec succés"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Mot de passe incorrecte"}, status=400)

    except Exception as e:
        return Response({"message" : "Une erreur est survenue"}, status=500)