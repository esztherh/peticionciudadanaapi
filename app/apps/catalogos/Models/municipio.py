from django.db import models
from django.urls import reverse


class Municipio(models.Model):
    municipio = models.CharField('Municipio', max_length=100)


    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"

    def __str__(self):
        return self.municipio

    def get_absolute_url(self):
        return reverse("Municipio_detail", kwargs={"pk": self.pk})
