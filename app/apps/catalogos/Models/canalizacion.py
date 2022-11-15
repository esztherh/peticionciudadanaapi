from django.db import models
from django.urls import reverse

from apps.catalogos.models import Medios_Captacion


class Tipo_Dependencia(models.Model):
    tipo_dependencia = models.CharField('Tipo de Dependencia', max_length=50)

    class Meta:
        verbose_name = "Tipo de Dependencia"
        verbose_name_plural = "Tipos de Dependencias"

    def __str__(self):
        return self.tipo_dependencia

    def get_absolute_url(self):
        return reverse("Tipo_Dependencia_detail", kwargs={"pk": self.pk})


class Tipo_Formato(models.Model):
    tipo_formato = models.CharField('Tipo de Formato', max_length=50)

    class Meta:
        verbose_name = "Tipo de Formato"
        verbose_name_plural = "Tipos de Formatos"

    def __str__(self):
        return self.tipo_formato

    def get_absolute_url(self):
        return reverse("Tipo_Formato_detail", kwargs={"pk": self.pk})


class Canalizaciones(models.Model):
    dependencia = models.CharField('Dependencia', max_length=150)
    titular = models.CharField('Titular', max_length=50)
    tipo_dependencia = models.ForeignKey(Tipo_Dependencia, verbose_name='Tipo de Dependencia', on_delete=models.CASCADE)
    tipo_formato = models.ForeignKey(Tipo_Formato, verbose_name='Tipo de Formato', on_delete=models.CASCADE)
    medios_capacitaciones = models.ManyToManyField(Medios_Captacion)

    class Meta:
        verbose_name = "Canalización"
        verbose_name_plural = "Canalizaciones"

    def __str__(self):
        return self.dependencia

    def get_absolute_url(self):
        return reverse("Canalizaciones_detail", kwargs={"pk": self.pk})
