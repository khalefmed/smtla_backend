from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Rotation,
    TypeMateriel,
    RotationEntrante,
    RotationSortante,
    Client,
    Fournisseur,
    ExpressionBesoin,
    ItemExpressionBesoin,
    NoteDeFrais,
    ItemNoteDeFrais,
    Devis,
    ItemDevis,
    Facture,
    ItemFacture,
    BonCommande,
    BAD,
    ItemBAD,
    ItemBonCommande,
    Utilisateur,
    DocumentArchive
)


@admin.register(TypeMateriel)
class TypeMaterielAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "description", "date_creation")
    search_fields = ("nom", "description")
    ordering = ("nom",)
    readonly_fields = ("date_creation",)



@admin.register(Rotation)
class RotationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type_produit",
        "type",
        "numero_bordereau",
        "camion",
        "quantite",
        "date_rotation",
    )
    list_filter = ("type", "type_produit", "date_rotation")
    search_fields = ("numero_bordereau", "camion", "type_produit__nom")
    ordering = ("-date_rotation",)
    readonly_fields = ("date_creation",)



@admin.register(RotationEntrante)
class RotationEntranteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "type_materiel",
        "numero_bordereau",
        "camion",
        "quantite",
        "date_arrivee",
    )
    list_filter = ("client", "type_materiel", "date_arrivee")
    search_fields = ("numero_bordereau", "camion", "client__nom", "type_materiel__nom")
    ordering = ("-date_arrivee",)
    readonly_fields = ("date_creation",)



@admin.register(RotationSortante)
class RotationSortanteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "type_materiel",
        "numero_bordereau",
        "camion",
        "quantite",
        "date_sortie",
    )
    list_filter = ("client", "type_materiel", "date_sortie")
    search_fields = ("numero_bordereau", "camion", "client__nom", "type_materiel__nom")
    ordering = ("-date_sortie",)
    readonly_fields = ("date_creation",)



@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "telephone", "email", "nif")
    search_fields = ("nom", "telephone", "email", "nif")
    ordering = ("nom",)



@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "raison_sociale", "telephone", "email", "nif")
    search_fields = ("nom", "raison_sociale", "telephone", "email", "nif")
    ordering = ("nom",)



class ItemExpressionBesoinInline(admin.TabularInline):
    model = ItemExpressionBesoin
    extra = 1

@admin.register(ExpressionBesoin)
class ExpressionBesoinAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "nom_demandeur",      
        "direction",         
        "client_beneficiaire",
        "navire",
        "status",
        "date_creation",
        "montant_total_affiche",
    )
    
    list_filter = ("status", "direction", "affectation", "devise", "tva", "date_creation")
    
    search_fields = ("reference", "nom_demandeur", "client_beneficiaire__nom", "bl_awb", "navire")
    
    ordering = ("-date_creation",)
    
    readonly_fields = (
        "reference", 
        "date_creation", 
        "montant_total_affiche", 
        "createur", 
        "valideur", 
        "date_validation"
    )
    
    inlines = [ItemExpressionBesoinInline]

    fieldsets = (
        ("Identification", {
            "fields": ("reference", "status", "date_creation")
        }),
        ("Détails du Demandeur", {
            "fields": ("nom_demandeur", "direction", "affectation"),
            "description": "Informations sur l'origine du besoin."
        }),
        ("Détails Logistiques & Client", {
            "fields": ("client_beneficiaire", "bl_awb", "navire", "eta")
        }),
        ("Finances", {
            "fields": ("devise", "tva", "montant_total_affiche")
        }),
        ("Validation & Traçabilité", {
            "fields": ("createur", "valideur", "date_validation"),
            "classes": ("collapse",) 
        }),
    )

    def montant_total_affiche(self, obj):
        return f"{obj.montant_total} {obj.devise}"
    
    montant_total_affiche.short_description = "Montant Total"

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.createur = request.user
        super().save_model(request, obj, form, change)




class ItemNoteDeFraisInline(admin.TabularInline):
    model = ItemNoteDeFrais
    extra = 0 

@admin.register(NoteDeFrais)
class NoteDeFraisAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "get_client",   
        "get_navire",   
        "status",
        "date_creation",
        "createur",
        "montant_total_affiche",
    )
    
    list_filter = (
        "status", 
        "expression_besoin__devise", 
        "expression_besoin__tva", 
        "date_creation"
    )
    
    search_fields = (
        "reference", 
        "expression_besoin__client_beneficiaire__nom", 
        "expression_besoin__bl_awb", 
        "expression_besoin__navire"
    )
    
    ordering = ("-date_creation",)
    
    readonly_fields = (
        "reference", 
        "expression_besoin",
        "get_client",
        "get_navire",
        "get_devise",
        "date_creation", 
        "montant_total_affiche", 
        "createur", 
        "valideur", 
        "date_validation"
    )
    
    inlines = [ItemNoteDeFraisInline]


    def get_client(self, obj):
        return obj.expression_besoin.client_beneficiaire
    get_client.short_description = "Client / Bénéficiaire"
    get_client.admin_order_field = 'expression_besoin__client_beneficiaire'

    def get_navire(self, obj):
        return obj.expression_besoin.navire
    get_navire.short_description = "Navire"
    get_navire.admin_order_field = 'expression_besoin__navire'

    def get_devise(self, obj):
        return obj.expression_besoin.get_devise_display()
    get_devise.short_description = "Devise"

    def montant_total_affiche(self, obj):
        return f"{obj.montant_total} {obj.expression_besoin.devise}"
    montant_total_affiche.short_description = "Montant total"



class ItemDevisInline(admin.TabularInline):
    model = ItemDevis
    extra = 1


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "client",
        "port_arrive",
        "vessel",
        "status",
        "date_creation",
        "createur",
        "valideur",
        "montant_total_affiche",
    )
    list_filter = ("status", "devise", "tva", "date_creation")
    search_fields = ("reference", "client__nom", "bl", "vessel")
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "montant_total_affiche", "createur", "valideur", "date_validation")
    inlines = [ItemDevisInline]

    def montant_total_affiche(self, obj):
        return obj.montant_total
    montant_total_affiche.short_description = "Montant total"



class ItemFactureInline(admin.TabularInline):
    model = ItemFacture
    extra = 1


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "client",
        "port_arrive",
        "vessel",
        "status",
        "est_privee",
        "date_creation",
        "createur",
        "valideur",
        "montant_total_affiche",
    )
    list_filter = ("status", "est_privee", "devise", "tva", "date_creation")
    search_fields = ("reference", "client__nom", "bl", "vessel")
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "montant_total_affiche", "createur", "valideur", "date_validation")
    inlines = [ItemFactureInline]

    def montant_total_affiche(self, obj):
        return obj.montant_total
    montant_total_affiche.short_description = "Montant total"



class ItemBonCommandeInline(admin.TabularInline):
    model = ItemBonCommande
    extra = 1


@admin.register(BonCommande)
class BonCommandeAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "fournisseur",
        "date",
        "status",
        "tva",
        "date_creation",
        "createur",
        "valideur",
        "montant_total_affiche",
    )
    list_filter = ("status", "tva", "date_creation", "date")
    search_fields = ("reference", "fournisseur__nom", "objet_commande")
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "montant_total_affiche", "createur", "valideur", "date_validation")
    inlines = [ItemBonCommandeInline]

    def montant_total_affiche(self, obj):
        return obj.montant_total
    montant_total_affiche.short_description = "Montant total"




class ItemBADInline(admin.TabularInline):
    model = ItemBAD
    extra = 1
    readonly_fields = ("createur", "valideur")
    fields = ("bl", "package_number", "weight", "nombre_jours", "createur", "valideur")

@admin.register(BAD)
class BADAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "client",
        "facture_liee",
        "date",
        "date_expiration",
        "nom_representant",
        "date_creation",
    )
    list_filter = ("date", "date_expiration", "client")
    search_fields = (
        "reference", 
        "client__nom", 
        "facture__reference", 
        "nom_representant"
    )
    ordering = ("-date_creation",)
    
    readonly_fields = ("date_creation",)
    
    inlines = [ItemBADInline]

    def facture_liee(self, obj):
        if obj.facture:
            return obj.facture.reference
        return "N/A"
    facture_liee.short_description = "Facture associée"

@admin.register(ItemBAD)
class ItemBADAdmin(admin.ModelAdmin):
    """Permet de visualiser les items individuellement si besoin"""
    list_display = ("bl", "bad", "package_number", "weight", "createur", "valideur")
    list_filter = ("bad__client", "createur")
    search_fields = ("bl", "bad__reference")



@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = (
        "username",
        "prenom",
        "nom",
        "telephone",
        "type",
        "is_staff",
        "is_active",
    )
    list_filter = ("type", "is_staff", "is_active")
    search_fields = ("username", "prenom", "nom", "telephone")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informations supplémentaires",
            {
                "fields": (
                    "prenom",
                    "nom",
                    "telephone",
                    "type",
                )
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")



@admin.register(DocumentArchive)
class DocumentArchiveAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "type_doc",
        "cree_par",
        "date_upload",
        "get_taille_fichier",
    )
    list_filter = ("type_doc", "date_upload", "cree_par")
    search_fields = ("titre", "description")
    ordering = ("-date_upload",)
    
    readonly_fields = ("date_upload", "cree_par")

    def get_taille_fichier(self, obj):
        try:
            size = obj.fichier.size / 1024
            return f"{size:.2f} Ko"
        except:
            return "N/A"
    get_taille_fichier.short_description = "Taille"

    def save_model(self, request, obj, form, change):
        """Assigne automatiquement l'utilisateur qui télécharge le document via l'admin"""
        if not obj.pk:  
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)



admin.site.site_header = "SMTLA - Administration"
admin.site.site_title = "SMTLA Admin"
admin.site.index_title = "Tableau de bord d'administration"