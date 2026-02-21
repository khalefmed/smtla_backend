from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ==================== DASHBOARD ====================
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # ==================== TYPE MATERIEL (Spec 5) ====================
    path('types-materiel/', TypeMaterielListCreateView.as_view(), name='type-materiel-list-create'),
    path('types-materiel/<int:pk>/', TypeMaterielRetrieveUpdateDeleteView.as_view(), name='type-materiel-detail'),
    path('types-materiel/recherche/', TypeMaterielRechercheView.as_view(), name='type-materiel-recherche'),
    
    # ==================== ROTATION ====================
    path('rotations/', RotationListCreateView.as_view(), name='rotation-list-create'),
    path('rotations/<int:pk>/', RotationRetrieveUpdateDeleteView.as_view(), name='rotation-detail'),
    path('rotations/par-type/', RotationParTypeView.as_view(), name='rotations-par-type'),
    
    # ==================== ROTATIONS ENTRANTES (Spec 6) ====================
    path('rotations-entrantes/', RotationEntranteListCreateView.as_view(), name='rotation-entrante-list-create'),
    path('rotations-entrantes/<int:pk>/', RotationEntranteRetrieveUpdateDeleteView.as_view(), name='rotation-entrante-detail'),
    path('rotations-entrantes/rapport/', RotationEntranteRapportView.as_view(), name='rotation-entrante-rapport'),
    
    # ==================== ROTATIONS SORTANTES (Spec 7) ====================
    path('rotations-sortantes/', RotationSortanteListCreateView.as_view(), name='rotation-sortante-list-create'),
    path('rotations-sortantes/<int:pk>/', RotationSortanteRetrieveUpdateDeleteView.as_view(), name='rotation-sortante-detail'),
    path('rotations-sortantes/rapport/', RotationSortanteRapportView.as_view(), name='rotation-sortante-rapport'),
    
    # ==================== CLIENTS ====================
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientRetrieveUpdateDeleteView.as_view(), name='client-detail'),
    path('clients/recherche/', ClientRechercheView.as_view(), name='client-recherche'),
    
    # ==================== FOURNISSEURS (Spec 9) ====================
    path('fournisseurs/', FournisseurListCreateView.as_view(), name='fournisseur-list-create'),
    path('fournisseurs/<int:pk>/', FournisseurRetrieveUpdateDeleteView.as_view(), name='fournisseur-detail'),
    path('fournisseurs/recherche/', FournisseurRechercheView.as_view(), name='fournisseur-recherche'),
    
    # ==================== EXPRESSIONS DE BESOIN (Spec 1) ====================
    path('expressions-besoin/', ExpressionBesoinListCreateView.as_view(), name='expression-besoin-list-create'),
    path('expressions-besoin/<int:pk>/', ExpressionBesoinRetrieveUpdateDeleteView.as_view(), name='expression-besoin-detail'),
    path('expressions-besoin/<int:pk>/valider/', ExpressionBesoinValiderView.as_view(), name='expression-besoin-valider'),
    
    # ==================== NOTES DE FRAIS (Spec 2) ====================
    path('notes-frais/', NoteDeFraisListCreateView.as_view(), name='note-frais-list-create'),
    path('notes-frais/<int:pk>/', NoteDeFraisRetrieveUpdateDeleteView.as_view(), name='note-frais-detail'),
    path('notes-frais/<int:pk>/valider/', NoteDeFraisValiderView.as_view(), name='note-frais-valider'),
    path('notes-frais/depuis-expression/<int:expression_id>/', NoteDeFraisCreerDepuisExpressionView.as_view(), name='note-frais-depuis-expression'),
    path('notes-frais/par-devise/', NoteDeFraisParDeviseView.as_view(), name='notes-frais-par-devise'),
    path('notes-frais/<int:pk>/ajouter-item/', NoteDeFraisAjouterItemView.as_view(), name='note-frais-ajouter-item'),
    path('notes-frais/<int:pk>/export-xlsx/', NoteDeFraisExportXlsxView.as_view(), name='note-frais-export-xlsx'),
    path('notes-frais/<int:pk>/export-pdf/', NoteDeFraisExportPdfView.as_view(), name='note-frais-export-pdf'),
    
    # ==================== DEVIS (Spec 4) ====================
    path('devis/', DevisListCreateView.as_view(), name='devis-list-create'),
    path('devis/<int:pk>/', DevisRetrieveUpdateDeleteView.as_view(), name='devis-detail'),
    path('devis/<int:pk>/valider/', DevisValiderView.as_view(), name='devis-valider'),
    path('devis/client/<int:client_id>/', DevisParClientView.as_view(), name='devis-par-client'),
    path('devis/<int:pk>/ajouter-item/', DevisAjouterItemView.as_view(), name='devis-ajouter-item'),
    path('devis/<int:pk>/convertir-en-facture/', DevisConvertirEnFactureView.as_view(), name='devis-convertir-facture'),
    
    # ==================== FACTURES (Spec 3) ====================
    path('factures/', FactureListCreateView.as_view(), name='facture-list-create'),
    path('factures/<int:pk>/', FactureRetrieveUpdateDeleteView.as_view(), name='facture-detail'),
    path('factures/<int:pk>/valider/', FactureValiderView.as_view(), name='facture-valider'),
    path('factures/client/<int:client_id>/', FactureParClientView.as_view(), name='factures-par-client'),
    path('factures/<int:pk>/ajouter-item/', FactureAjouterItemView.as_view(), name='facture-ajouter-item'),
    
    # ==================== BONS DE COMMANDE (Spec 10) ====================
    path('bons-commande/', BonCommandeListCreateView.as_view(), name='bon-commande-list-create'),
    path('bons-commande/<int:pk>/', BonCommandeRetrieveUpdateDeleteView.as_view(), name='bon-commande-detail'),
    path('bons-commande/<int:pk>/valider/', BonCommandeValiderView.as_view(), name='bon-commande-valider'),
    path('bons-commande/<int:pk>/ajouter-item/', BonCommandeAjouterItemView.as_view(), name='bon-commande-ajouter-item'),

    # ==================== BONS À DÉLIVRER (BAD) ====================
    path('bads/', BADListCreateView.as_view(), name='bad-list-create'),
    path('bads/<int:pk>/', BADRetrieveUpdateDeleteView.as_view(), name='bad-detail'),
    path('bads/items/<int:item_id>/valider/', BADValiderItemView.as_view(), name='bad-item-valider'),
    path('bads/facture/<int:facture_id>/', BADParFactureView.as_view(), name='bad-par-facture'),
    path('bads/<int:pk>/export-pdf/', BADExportPdfView.as_view(), name='bad-export-pdf'),

    # ==================== ARCHIVES DOCUMENTAIRES (GED) ====================
    path('archives/', DocumentArchiveListCreateView.as_view(), name='archive-list-create'),
    path('archives/<int:pk>/', DocumentArchiveRetrieveUpdateDeleteView.as_view(), name='archive-detail'),
    path('archives/recherche/', DocumentArchiveRechercheView.as_view(), name='archive-recherche'),
    
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