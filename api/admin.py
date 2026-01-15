from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


class DossierAdmin(admin.ModelAdmin):
    list_display = ("id", "numero", "titre", "date_creation", "etape")
    list_filter = ("etape", "date_creation")
    search_fields = ("numero", "titre", "libelle")
    ordering = ("-date_creation",)

    actions = ["mettre_en_archive_finale"]

    def mettre_en_archive_finale(self, request, queryset):
        queryset.update(etape="archive_final")
    mettre_en_archive_finale.short_description = "Mettre les dossiers en archive finale"



class PieceJointeAdmin(admin.ModelAdmin):
    list_display = ("id", "titre", "dossier", "date_creation", "fichier")
    list_filter = ("date_creation",)
    search_fields = ("titre",)

    def voir_pdf(self, obj):
        return obj.fichier.url

    readonly_fields = ("path", "date_creation")


class BoiteArchiveAdmin(admin.ModelAdmin):
    list_display = ("id", "reference", "date_creation", "taille")
    list_filter = ("date_creation",)
    search_fields = ("reference",)


    readonly_fields = ("reference", "date_creation")


class UtilisateurAdmin(UserAdmin):
    list_display = (
        "username",
        "telephone",
        "type",
        "is_staff",
        "is_active",
        "date_joined",
    )

    search_fields = ("username", "telephone")
    list_filter = ("is_staff", "is_active", "type")

    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {"fields": ("telephone", "type")}),
    )


# ─────────────────────────────
# Configuration interface
# ─────────────────────────────

admin.site.site_header = "GED"
admin.site.site_title = "Gestion Électronique des Documents"
admin.site.index_title = "Administration GED"


admin.site.register(Dossier, DossierAdmin)
admin.site.register(PieceJointe, PieceJointeAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(BoiteArchive, BoiteArchiveAdmin )