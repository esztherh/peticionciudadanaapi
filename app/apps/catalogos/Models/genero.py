from django.db import models
from django.urls import reverse


class Genero(models.Model):
    genero = models.CharField('Género', max_length=20)


    class Meta:
        verbose_name = "Genero"
        verbose_name_plural = "Generos"

    def __str__(self):
        return self.genero

    def get_absolute_url(self):
        return reverse("Genero_detail", kwargs={"pk": self.pk})
