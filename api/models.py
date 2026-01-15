from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

from datetime import datetime
from django.db.models import Max  
from cloudinary_storage.storage import RawMediaCloudinaryStorage 


import cloudinary
import cloudinary.utils
import os
from urllib.parse import urlparse




class Dossier(models.Model):

    ETAPES = [
        ('numerisation', 'Numérisation'),
        ('validation', 'Validation'),
        ('archive_temporaire', 'Archive temporaire'),
        ('archive_physique', 'Archive physique'),
        ('archive_final', 'Archive final'),
        ('archive_finale', 'Archive finale'),
    ]

    numero = models.CharField(max_length=15, unique=True, editable=False)

    titre = models.CharField(max_length=255)

    date_creation = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=100, blank=True, null=True, default='Annotation')
    

    libelle = models.TextField()

    etape = models.CharField(
        max_length=30,
        choices=ETAPES,
        default='numerisation'
    )

    boite = models.ForeignKey(
        'BoiteArchive',
        on_delete=models.CASCADE,
        related_name='dossiers',
        null=True,
        blank=True
    )

    def generer_numero(self):
        annee = datetime.now().year

        dernier = Dossier.objects.filter(
            numero__endswith=f"/{annee}"
        ).aggregate(max_num=Max('numero'))

        if dernier['max_num']:
            last_counter = int(dernier['max_num'].split('/')[0])
            compteur = last_counter + 1
        else:
            compteur = 1

        return f"{compteur:04d}/{annee}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generer_numero()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} - {self.titre}"





class PieceJointe(models.Model):
    fichier = models.FileField(
        upload_to='dossiers/pieces/',
        storage=RawMediaCloudinaryStorage()
    )
    titre = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='pieces'
    )

    @property
    def path(self):
        if not self.fichier:
            return ""
        
        try:
            # Get the original URL
            url = self.fichier.url
            
            # Extract public_id from URL
            # Example: https://res.cloudinary.com/djcpxnvbl/raw/upload/v1/dossiers/pieces/Cryptomonnaies_F_nfwljs.pdf
            parsed = urlparse(url)
            path_parts = parsed.path.split('/upload/')
            
            if len(path_parts) == 2:
                # Get everything after /upload/ and remove version (v1, v1767791195, etc)
                after_upload = path_parts[1]
                # Remove version number (v followed by digits and /)
                import re
                public_id_with_ext = re.sub(r'^v\d+/', '', after_upload)
                
                # Remove file extension to get public_id
                public_id = os.path.splitext(public_id_with_ext)[0]
                
                # Get file extension
                file_extension = os.path.splitext(public_id_with_ext)[1].lower()
                
                # Determine resource type
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
                resource_type = 'image' if file_extension in image_extensions else 'raw'
                
                # Generate signed URL with type='authenticated' instead of sign_url
                signed_url, options = cloudinary.utils.cloudinary_url(
                    public_id,
                    resource_type=resource_type,
                    type='upload',
                    sign_url=True,
                    secure=True
                )
                
                return signed_url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            pass
        
        # Fallback to original URL
        return self.fichier.url

    def __str__(self):
        return self.titre
    



class BoiteArchive(models.Model):
    reference = models.IntegerField(unique=True, editable=False)
    taille = models.IntegerField(help_text="Taille en nombre de dossiers", default=50)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def generer_reference(self):
        """Génère la prochaine référence disponible"""
        dernier = BoiteArchive.objects.aggregate(max_ref=Max('reference'))
        
        if dernier['max_ref'] is not None:
            return dernier['max_ref'] + 1
        else:
            return 1  # Première boîte commence à 1
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.reference:  # Seulement lors de la création
            self.reference = self.generer_reference()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Boîte {self.reference}"
    



class Utilisateur(AbstractUser):
    telephone = models.CharField(max_length=8, unique=True)
    type = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Administrateur'),
            ('numerisateur', 'Numérisateur'),
            ('validateur', 'Validateur'),
            ('archiviste', 'Archiviste'),
        ],
        default='numerisateur'
    )

    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    # def save(self, *args, **kwargs):
    #     # hash password only during first creation
    #     if not self.pk and self.password:
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)