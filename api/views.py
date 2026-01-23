from datetime import timedelta
from rest_framework import generics
import csv, io
import os
from django.conf import settings
from django.http import HttpResponse

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

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password

from rest_framework.pagination import PageNumberPagination

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from django.db.models import Q, Avg, Sum, Count, F
from django.core.files.storage import default_storage
from django.db.models import Sum, Count, Q, FloatField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
import calendar
from rest_framework import status
from openpyxl import load_workbook

import tempfile
import subprocess
from django.http import FileResponse
from django.shortcuts import get_object_or_404



class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.type
        stats = {}

        # 1. Statistiques Produits (Agent Port, DO, DG)
        if role in ['agent_port', 'directeur_operations', 'directeur_general']:
            stats['produits'] = {
                'total': Produit.objects.count(),
                'en_stock': Produit.objects.filter(statut='arrive').count(),
                'sortis': Produit.objects.filter(statut='sortie').count(),
            }

        # 2. Statistiques Clients (Agent Port, Comptable, DO, DG)
        if role in ['agent_port', 'comptable', 'directeur_operations', 'directeur_general']:
            stats['clients'] = {
                'total': Client.objects.count(),
            }

        # 3. Statistiques Note de Frais (Assistant, Comptable, DO, DG)
        if role in ['assistant', 'comptable', 'directeur_operations', 'directeur_general']:
            stats['notes_frais'] = {
                'en_attente': NoteDeFrais.objects.filter(status='attente').count(),
                'validees': NoteDeFrais.objects.filter(status='valide').count(),
                'total_montant': NoteDeFrais.objects.filter(status='valide').aggregate(Sum('items__montant'))['items__montant__sum'] or 0
            }

        # 4. Statistiques Devis & Factures (Comptable, DO, DG)
        if role in ['comptable', 'directeur_operations', 'directeur_general']:
            stats['devis'] = {
                'total': Devis.objects.count(),
                'somme_totale': sum(d.montant_total for d in Devis.objects.all())
            }
            stats['factures'] = {
                'total': Facture.objects.count(),
                'somme_totale': sum(f.montant_total for f in Facture.objects.all())
            }

        return Response(stats)


# ==================== VUES PRODUIT ====================

class ProduitListCreateView(generics.ListCreateAPIView):
    """Liste tous les produits ou crée un nouveau produit"""
    queryset = Produit.objects.all().order_by('-date_arrivee')
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]


class ProduitRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime un produit spécifique"""
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]


class ProduitParStatutView(generics.ListAPIView):
    """Liste les produits filtrés par statut"""
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        statut = self.request.query_params.get('statut')
        queryset = Produit.objects.all().order_by('-date_arrivee')
        
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset


class ProduitChangerStatutView(APIView):
    """Change le statut d'un produit (arrive -> sortie)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            produit = Produit.objects.get(pk=pk)
        except Produit.DoesNotExist:
            return Response(
                {"detail": "Produit introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        nouveau_statut = request.data.get('statut')
        date_sortie = request.data.get('date_sortie')
        
        if not nouveau_statut:
            return Response(
                {"detail": "Le statut est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if nouveau_statut == 'sortie' and not date_sortie:
            return Response(
                {"detail": "La date de sortie est requise pour le statut 'sortie'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        produit.statut = nouveau_statut
        if date_sortie:
            produit.date_sortie = date_sortie
        produit.save()
        
        return Response(
            ProduitSerializer(produit).data,
            status=status.HTTP_200_OK
        )


# ==================== VUES CLIENT ====================

class ClientListCreateView(generics.ListCreateAPIView):
    """Liste tous les clients ou crée un nouveau client"""
    queryset = Client.objects.all().order_by('nom')
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


class ClientRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime un client spécifique"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


class ClientRechercheView(generics.ListAPIView):
    """Recherche de clients par nom, téléphone ou email"""
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Client.objects.filter(
            Q(nom__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(nif__icontains=query)
        ).order_by('nom')


# ==================== VUES NOTE DE FRAIS ====================

class NoteDeFraisListCreateView(generics.ListCreateAPIView):
    """Liste toutes les notes de frais ou crée une nouvelle"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NoteDeFraisCreateSerializer
        return NoteDeFraisSerializer

    def get_queryset(self):
        user = self.request.user
        # Base queryset ordered by date
        queryset = NoteDeFrais.objects.all().order_by('-date_creation')

        # Logic for "Comptable": only show validated notes
        if hasattr(user, 'type') and user.type == 'comptable':
            return queryset.filter(status='valide')
        
        # For all other user types, return everything
        return queryset


class NoteDeFraisRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime une note de frais spécifique"""
    queryset = NoteDeFrais.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NoteDeFraisCreateSerializer   # même serializer que l'ajout
        return NoteDeFraisSerializer


class NoteDeFraisStatusUpdateView(APIView):
    """Permet de valider ou rejeter une note de frais"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        note = get_object_or_404(NoteDeFrais, pk=pk)
        nouveau_statut = request.data.get('status')

        if nouveau_statut not in ['valide', 'rejete', 'attente']:
            return Response({"error": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

        # Seuls certains rôles devraient pouvoir valider (ex: DG ou Comptable)
        # Vous pouvez ajouter une vérification ici: if request.user.type != 'directeur_general': ...
        
        note.status = nouveau_statut
        note.save()
        
        return Response({
            "message": f"Note {nouveau_statut} avec succès",
            "status": note.status
        })


class NoteDeFraisParDeviseView(generics.ListAPIView):
    """Liste les notes de frais par devise"""
    serializer_class = NoteDeFraisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        devise = self.request.query_params.get('devise')
        queryset = NoteDeFrais.objects.all().order_by('-date_creation')
        
        if devise:
            queryset = queryset.filter(devise=devise)
        
        return queryset


class NoteDeFraisAjouterItemView(APIView):
    """Ajoute un item à une note de frais existante"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            note = NoteDeFrais.objects.get(pk=pk)
        except NoteDeFrais.DoesNotExist:
            return Response(
                {"detail": "Note de frais introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ItemNoteDeFraisSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(note_de_frais=note)
            return Response(
                NoteDeFraisSerializer(note).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




# views.py


class NoteDeFraisExportXlsxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            note = NoteDeFrais.objects.get(pk=pk)
        except NoteDeFrais.DoesNotExist:
            return Response({"detail": "Note de frais introuvable"}, status=404)

        template_path = os.path.join(settings.BASE_DIR, "templates", "NOTE-DE-DEPENSES-MRU.xlsx")
        wb = load_workbook(template_path)
        ws = wb.active  # Feuil1

        # Header zone (adapt cells to your real template)
        # In your sample: reference is at last column, date in header, etc. [file:1]
        ws["J1"] = note.reference          # 0002/2025 in your example [file:1]
        ws["J2"] = note.date_creation.date().strftime("%d/%m/%Y")  # Date [file:1]
        # If you later have user fields (Nom & Prénom, Direction, etc.), fill them here.

        # Table header line is "Désignation | Nourriture | Hebergement ..." [file:1]
        # In your sample, the first data row is below that: "m'ain d'eouvre Fixation Aluminiun ..." [file:1]
        # Suppose this is row 7 (adjust to your template).
        start_row = 7

        # Reset previous dynamic rows if needed (optional)

        current_row = start_row
        for item in note.items.all():
            # Column mapping: A=Designation, C=Nourriture, D=Hebergement, E=Medicament, F=Carburant,
            # G=Entretien, H=Telecom, I=Avance, J=Divers, per your header. [file:1]
            ws[f"A{current_row}"] = item.get_type_display()  # or real description if you add it
            col_map = {
                "nourriture": "C",
                "hebergement": "D",
                "medicament": "E",
                "carburant": "F",
                "entretien": "G",
                "telecom": "H",
                "avance": "I",
                "divers": "J",
            }
            col = col_map.get(item.type)
            if col:
                ws[f"{col}{current_row}"] = float(item.montant)

            current_row += 1

        # TOTAL row in your template already exists with formulas; if needed you can update cells
        # In your sample: last TOTAL at bottom "TOTAL 400.00 [MRU]" etc. [file:1]
        # Example: assume global total (all columns) is at J9, J10, J12:
        total = float(note.montant_total)
        ws["J9"] = total             # TOTAL ... [file:1]
        ws["J10"] = f"{total} {note.devise}"  # MONTANT HT/MRU [file:1]
        ws["J12"] = f"{total} {note.devise}"  # MONTANT TTC [file:1]

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"{note.reference}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response


class NoteDeFraisExportPdfView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            note = NoteDeFrais.objects.get(pk=pk)
        except NoteDeFrais.DoesNotExist:
            return Response({"detail": "Note de frais introuvable"}, status=404)

        template_path = os.path.join(settings.BASE_DIR, "templates", "NOTE-DE-DEPENSES-MRU.xlsx")
        wb = load_workbook(template_path)
        ws = wb.active

        # Same filling as in XLSX view (copy/paste the mapping)
        ws["J1"] = note.reference
        ws["J2"] = note.date_creation.date().strftime("%d/%m/%Y")

        start_row = 7
        current_row = start_row
        col_map = {
            "nourriture": "C",
            "hebergement": "D",
            "medicament": "E",
            "carburant": "F",
            "entretien": "G",
            "telecom": "H",
            "avance": "I",
            "divers": "J",
        }
        for item in note.items.all():
            ws[f"A{current_row}"] = item.get_type_display()
            col = col_map.get(item.type)
            if col:
                ws[f"{col}{current_row}"] = float(item.montant)
            current_row += 1

        total = float(note.montant_total)
        ws["J9"] = total
        ws["J10"] = f"{total} {note.devise}"
        ws["J12"] = f"{total} {note.devise}"

        with tempfile.TemporaryDirectory() as tmpdir:
            xlsx_path = os.path.join(tmpdir, "note.xlsx")
            pdf_path = os.path.join(tmpdir, "note.pdf")
            wb.save(xlsx_path)

            cmd = [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                tmpdir,
                xlsx_path,
            ]
            subprocess.run(cmd, check=True)

            return FileResponse(
                open(pdf_path, "rb"),
                as_attachment=True,
                filename=f"{note.reference}.pdf",
                content_type="application/pdf",
            )



# ==================== VUES DEVIS ====================

class DevisListCreateView(generics.ListCreateAPIView):
    """Liste tous les devis ou crée un nouveau devis"""
    queryset = Devis.objects.all().order_by('-date_creation')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DevisCreateSerializer
        return DevisSerializer


class DevisRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime un devis spécifique"""
    queryset = Devis.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DevisDetailSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return DevisCreateSerializer
        return DevisSerializer


class DevisParClientView(generics.ListAPIView):
    """Liste les devis d'un client spécifique"""
    serializer_class = DevisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return Devis.objects.filter(client_id=client_id).order_by('-date_creation')


class DevisAjouterItemView(APIView):
    """Ajoute un item à un devis existant"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            devis = Devis.objects.get(pk=pk)
        except Devis.DoesNotExist:
            return Response(
                {"detail": "Devis introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ItemDevisSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(devis=devis)
            return Response(
                DevisDetailSerializer(devis).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DevisConvertirEnFactureView(APIView):
    """Convertit un devis en facture"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            devis = Devis.objects.get(pk=pk)
        except Devis.DoesNotExist:
            return Response(
                {"detail": "Devis introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with db_transaction.atomic():
            # Créer la facture
            facture = Facture.objects.create(
                client=devis.client,
                port_arrive=devis.port_arrive,
                vessel=devis.vessel,
                voyage=devis.voyage,
                eta=devis.eta,
                etd=devis.etd,
                bl=devis.bl,
                tva=devis.tva,
                devise=devis.devise
            )
            
            # Copier les items
            for item_devis in devis.items.all():
                ItemFacture.objects.create(
                    facture=facture,
                    libelle=item_devis.libelle,
                    prix_unitaire=item_devis.prix_unitaire,
                    quantite=item_devis.quantite
                )
        
        return Response(
            {
                "message": "Devis converti en facture avec succès",
                "facture": FactureDetailSerializer(facture).data
            },
            status=status.HTTP_201_CREATED
        )


# ==================== VUES FACTURE ====================

class FactureListCreateView(generics.ListCreateAPIView):
    """Liste toutes les factures ou crée une nouvelle facture"""
    queryset = Facture.objects.all().order_by('-date_creation')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FactureCreateSerializer
        return FactureSerializer


class FactureRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime une facture spécifique"""
    queryset = Facture.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FactureDetailSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return FactureCreateSerializer 
        return FactureSerializer


class FactureParClientView(generics.ListAPIView):
    """Liste les factures d'un client spécifique"""
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return Facture.objects.filter(client_id=client_id).order_by('-date_creation')


class FactureAjouterItemView(APIView):
    """Ajoute un item à une facture existante"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            facture = Facture.objects.get(pk=pk)
        except Facture.DoesNotExist:
            return Response(
                {"detail": "Facture introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ItemFactureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(facture=facture)
            return Response(
                FactureDetailSerializer(facture).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== VUES UTILISATEUR ====================

class UtilisateurListCreateView(generics.ListCreateAPIView):
    """Liste tous les utilisateurs ou crée un nouvel utilisateur"""
    queryset = Utilisateur.objects.all().order_by('nom', 'prenom')
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]


class UtilisateurRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Récupère, modifie ou supprime un utilisateur spécifique"""
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurCustomSerializer
    permission_classes = [IsAuthenticated]


class UtilisateurParTypeView(generics.ListAPIView):
    """Liste les utilisateurs filtrés par type"""
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        type_utilisateur = self.request.query_params.get('type')
        queryset = Utilisateur.objects.all().order_by('nom', 'prenom')
        
        if type_utilisateur:
            queryset = queryset.filter(type=type_utilisateur)
        
        return queryset


# ==================== AUTHENTIFICATION ====================

class SeConnecter(TokenObtainPairView):
    """Connexion de l'utilisateur avec username et mot de passe"""
    serializer_class = ConnexionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        mot_de_passe = serializer.validated_data['mot_de_passe']

        utilisateur = Utilisateur.objects.filter(username=username).first()
        
        if utilisateur:
            utilisateur = authenticate(request, username=username, password=mot_de_passe)
            if utilisateur:
                refresh = RefreshToken.for_user(utilisateur)
                
                utilisateur_data = UtilisateurSerializer(utilisateur).data
                
                data = {
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                    'utilisateur': utilisateur_data,
                }
                
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Nom d'utilisateur ou mot de passe incorrect"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {"detail": "Utilisateur introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def utilisateur_profil(request):
    """Récupère le profil de l'utilisateur connecté"""
    utilisateur = request.user
    try:
        utilisateur_data = UtilisateurSerializer(utilisateur)
        return JsonResponse(utilisateur_data.data)
    except Exception as e:
        return JsonResponse({
            "status": 500,
            "message": f"Échec du chargement du profil utilisateur: {e}"
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_informations(request):
    """Modifie les informations de l'utilisateur connecté"""
    user = request.user
    serializer = UtilisateurSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_mot_de_passe(request):
    """Modifie le mot de passe de l'utilisateur connecté"""
    utilisateur = request.user
    try:
        data = json.loads(request.body.decode('utf-8'))
        ancien = data.get('ancien', '')
        nouveau = data.get('nouveau', '')

        if not ancien or not nouveau:
            return Response(
                {"message": "L'ancien et le nouveau mot de passe sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if check_password(ancien, utilisateur.password):
            utilisateur.password = make_password(nouveau)
            utilisateur.save()

            return Response(
                {"message": "Mot de passe modifié avec succès"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Ancien mot de passe incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {"message": f"Une erreur est survenue: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== STATISTIQUES ====================

class StatistiquesGeneralesView(APIView):
    """Retourne les statistiques générales du système"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        stats = {
            'total_produits': Produit.objects.count(),
            'produits_arrives': Produit.objects.filter(statut='arrive').count(),
            'produits_sortis': Produit.objects.filter(statut='sortie').count(),
            'total_clients': Client.objects.count(),
            'total_devis': Devis.objects.count(),
            'total_factures': Facture.objects.count(),
            'total_notes_frais': NoteDeFrais.objects.count(),
            'total_utilisateurs': Utilisateur.objects.count(),
        }
        
        # Montants par devise (Devis)
        devis_par_devise = {}
        for devise_code, devise_nom in Devis.DEVISES:
            devis = Devis.objects.filter(devise=devise_code)
            total = sum(d.montant_total for d in devis)
            devis_par_devise[devise_code] = {
                'nom': devise_nom,
                'total': float(total),
                'nombre': devis.count()
            }
        
        # Montants par devise (Factures)
        factures_par_devise = {}
        for devise_code, devise_nom in Facture.DEVISES:
            factures = Facture.objects.filter(devise=devise_code)
            total = sum(f.montant_total for f in factures)
            factures_par_devise[devise_code] = {
                'nom': devise_nom,
                'total': float(total),
                'nombre': factures.count()
            }
        
        stats['devis_par_devise'] = devis_par_devise
        stats['factures_par_devise'] = factures_par_devise
        
        return Response(stats, status=status.HTTP_200_OK)


class StatistiquesClientView(APIView):
    """Retourne les statistiques d'un client spécifique"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, client_id):
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return Response(
                {"detail": "Client introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        devis = Devis.objects.filter(client=client)
        factures = Facture.objects.filter(client=client)
        
        stats = {
            'client': ClientSerializer(client).data,
            'total_devis': devis.count(),
            'total_factures': factures.count(),
            'montant_total_devis': sum(d.montant_total for d in devis),
            'montant_total_factures': sum(f.montant_total for f in factures),
        }
        
        return Response(stats, status=status.HTTP_200_OK)