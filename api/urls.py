
from django.urls import path
from .views import *


urlpatterns = [


    # Dossier
    path('dossiers/', DossierListCreateView.as_view()),
    path('dossiers/<int:pk>/', DossierRetrieveUpdateDeleteView.as_view()),
    path('dossiers/par-etape/', DossierParEtapeView.as_view()),

    # Gestion des boîtes d'archive
    path('boites/', BoiteArchiveListCreateView.as_view(), name='boite-list-create'),
    path('boites/<int:pk>/', BoiteArchiveRetrieveUpdateDeleteView.as_view(), name='boite-detail'),
    path('boites/disponibles/', BoiteArchiveDisponiblesView.as_view(), name='boites-disponibles'),
    path('boites/assigner/', AssignerBoiteView.as_view(), name='assigner-boite'),
    path('boites/retirer/', RetirerBoiteView.as_view(), name='retirer-boite'),
    path('boites/obtenir-ou-creer/', ObtenirOuCreerBoiteView.as_view(), name='obtenir-ou-creer-boite'), 

    # Étape
    path('dossiers/<int:pk>/etape/', DossierEtapeUpdateView.as_view()),

    # Pièces jointes
    path('pieces/', PieceJointeListCreateView.as_view()),
    path('pieces/<int:pk>/', PieceJointeRetrieveUpdateDeleteView.as_view()),

    # Utilisateur
    path('utilisateurs/', UtilisateurListCreateView.as_view()),
    path('utilisateurs/<int:pk>/', UtilisateurRetrieveUpdateDeleteView.as_view()),

    path('connexion/', SeConnecter.as_view(), name='connexion'),
    path('profil/', Utilisateur_profil, name='profile-view'),
    path('modifier_informations/', modifier_informations, name='modifier-informations'),
    path('modifier_mot_de_passe/', modifier_mot_de_passe, name='modifier-mot-passe'),
]
