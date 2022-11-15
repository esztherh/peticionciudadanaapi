from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.catalogos.models import Canalizaciones

class Usuario(AbstractUser):
    enlace_institucional = models.ForeignKey(Canalizaciones, verbose_name='Institución a la que pertenece', on_delete=models.CASCADE, related_name="enlace_institucional", blank=True, null=True)

    def __str__(self):
        return "%i - %s" % (self.pk, self.username)
