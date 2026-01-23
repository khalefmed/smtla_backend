from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Produit,
    Client,
    NoteDeFrais,
    ItemNoteDeFrais,
    Devis,
    ItemDevis,
    Facture,
    ItemFacture,
    Utilisateur
)

# ==================== PRODUITS ====================

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom",
        "camion",
        "quantite",
        "statut",
        "date_arrivee",
        "date_sortie",
    )
    list_filter = ("statut", "date_arrivee")
    search_fields = ("nom", "camion")
    ordering = ("-date_arrivee",)
    readonly_fields = ("date_arrivee",)

# ==================== CLIENTS ====================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "telephone", "email", "nif")
    search_fields = ("nom", "telephone", "email", "nif")
    ordering = ("nom",)

# ==================== NOTES DE FRAIS ====================

class ItemNoteDeFraisInline(admin.TabularInline):
    model = ItemNoteDeFrais
    extra = 1

@admin.register(NoteDeFrais)
class NoteDeFraisAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "date_creation",
        "devise",
        "tva",
        "montant_total_affiche",
    )
    list_filter = ("devise", "tva", "date_creation")
    search_fields = ("reference",)
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "montant_total_affiche")
    inlines = [ItemNoteDeFraisInline]

    def montant_total_affiche(self, obj):
        return obj.montant_total
    montant_total_affiche.short_description = "Montant total"

# ==================== DEVIS ====================

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
        "date_creation",
        "devise",
        "tva",
        "montant_total_affiche",
    )
    list_filter = ("devise", "tva", "date_creation")
    search_fields = ("reference", "client__nom", "bl")
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "montant_total_affiche")
    inlines = [ItemDevisInline]

    def montant_total_affiche(self, obj):
        return obj.montant_total
    montant_total_affiche.short_description = "Montant total"

# ==================== FACTURES ====================

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
        "date_creation",
        "devise",
        "tva",
        "montant_total_affiche",
    )
    list_filter = ("devise", "tva", "date_creation")
    search_fields = ("reference", "client__nom", "bl")
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "montant_total_affiche")
    inlines = [ItemFactureInline]

    def montant_total_affiche(self, obj):
        return obj.montant_total
    montant_total_affiche.short_description = "Montant total"

# ==================== UTILISATEURS ====================

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

# ==================== CONFIGURATION ADMIN ====================

admin.site.site_header = "SMTLA"
admin.site.site_title = "Administration"
admin.site.index_title = "Tableau de bord"