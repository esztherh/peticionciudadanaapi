from django.db import models
from django.urls import reverse


class Medios_Captacion(models.Model):
    medio_captacion = models.CharField('Medio de Captación', max_length=100)
    nomenclatura = models.CharField('Nomenclatura', max_length=10)

    class Meta:
        verbose_name = "Medio de Captación"
        verbose_name_plural = "Medios de Captación"

    def __str__(self):
        return self.medio_captacion

    def get_absolute_url(self):
        return reverse("MediosCaptacion_detail", kwargs={"pk": self.pk})
