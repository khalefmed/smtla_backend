from django.urls import path
from .views import *

urlpatterns = [

    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),

    
    # ==================== PRODUITS ====================
    path('produits/', ProduitListCreateView.as_view(), name='produit-list-create'),
    path('produits/<int:pk>/', ProduitRetrieveUpdateDeleteView.as_view(), name='produit-detail'),
    path('produits/par-statut/', ProduitParStatutView.as_view(), name='produits-par-statut'),
    path('produits/<int:pk>/changer-statut/', ProduitChangerStatutView.as_view(), name='produit-changer-statut'),
    
    # ==================== CLIENTS ====================
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientRetrieveUpdateDeleteView.as_view(), name='client-detail'),
    path('clients/recherche/', ClientRechercheView.as_view(), name='client-recherche'),
    
    # ==================== NOTES DE FRAIS ====================
    path('notes-frais/', NoteDeFraisListCreateView.as_view(), name='note-frais-list-create'),
    path('notes-frais/<int:pk>/', NoteDeFraisRetrieveUpdateDeleteView.as_view(), name='note-frais-detail'),
    path('notes-frais/par-devise/', NoteDeFraisParDeviseView.as_view(), name='notes-frais-par-devise'),
    path('notes-frais/<int:pk>/ajouter-item/', NoteDeFraisAjouterItemView.as_view(), name='note-frais-ajouter-item'),
    path('notes-frais/<int:pk>/status/', NoteDeFraisStatusUpdateView.as_view(), name='note-status-update'),

    path('notes-frais/<int:pk>/export-xlsx/', NoteDeFraisExportXlsxView.as_view(), name='note-frais-export-xlsx'),
    path('notes-frais/<int:pk>/export-pdf/', NoteDeFraisExportPdfView.as_view(), name='note-frais-export-pdf'),
    
    # ==================== DEVIS ====================
    path('devis/', DevisListCreateView.as_view(), name='devis-list-create'),
    path('devis/<int:pk>/', DevisRetrieveUpdateDeleteView.as_view(), name='devis-detail'),
    path('devis/client/<int:client_id>/', DevisParClientView.as_view(), name='devis-par-client'),
    path('devis/<int:pk>/ajouter-item/', DevisAjouterItemView.as_view(), name='devis-ajouter-item'),
    path('devis/<int:pk>/convertir-en-facture/', DevisConvertirEnFactureView.as_view(), name='devis-convertir-facture'),
    
    # ==================== FACTURES ====================
    path('factures/', FactureListCreateView.as_view(), name='facture-list-create'),
    path('factures/<int:pk>/', FactureRetrieveUpdateDeleteView.as_view(), name='facture-detail'),
    path('factures/client/<int:client_id>/', FactureParClientView.as_view(), name='factures-par-client'),
    path('factures/<int:pk>/ajouter-item/', FactureAjouterItemView.as_view(), name='facture-ajouter-item'),
    
    # ==================== UTILISATEURS ====================
    path('utilisateurs/', UtilisateurListCreateView.as_view(), name='utilisateur-list-create'),
    path('utilisateurs/<int:pk>/', UtilisateurRetrieveUpdateDeleteView.as_view(), name='utilisateur-detail'),
    path('utilisateurs/par-type/', UtilisateurParTypeView.as_view(), name='utilisateurs-par-type'),
    
    # ==================== AUTHENTIFICATION ====================
    path('connexion/', SeConnecter.as_view(), name='connexion'),
    path('profil/', utilisateur_profil, name='profil-view'),
    path('modifier-informations/', modifier_informations, name='modifier-informations'),
    path('modifier-mot-de-passe/', modifier_mot_de_passe, name='modifier-mot-passe'),
    
    # ==================== STATISTIQUES ====================
    path('statistiques/', StatistiquesGeneralesView.as_view(), name='statistiques-generales'),
    path('statistiques/client/<int:client_id>/', StatistiquesClientView.as_view(), name='statistiques-client'),
]