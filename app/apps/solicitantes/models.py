from django.db import models
from django.urls import reverse

from apps.catalogos.models import Genero, Municipio


class Solicitante(models.Model):
    # curp = models.CharField('CURP', max_length=18)
    clave_lector = models.CharField('Clave de Elector', max_length=18, blank=True, null=True)
    # rfc = models.CharField('RFC', max_length=13, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=10)
    nombre = models.CharField('Nombre', max_length=20)
    apellido_paterno = models.CharField('Apellido Paterno', max_length=20)
    apellido_materno = models.CharField('Apellido Materno', max_length=20)
    # organizacion = models.CharField('Organización', max_length=150, blank=True, null=True)
    # puesto_organizacion = models.CharField('Puesto en la Organización', max_length=150, blank=True, null=True)
    correo_electronico = models.CharField('Correo Electrónico', max_length=200, blank=True, null=True)
    calle = models.CharField('Calle', max_length=200)
    numero_exterior = models.CharField('Número Exterior', max_length=10)
    numero_interior = models.CharField('Número Interior', max_length=10, blank=True, null=True)
    codigo_postal = models.CharField('Código Postal', max_length=10)
    estado = models.CharField('Estado', max_length=50, default='Puebla')
    municipio = models.ForeignKey(Municipio, verbose_name='Municipio', on_delete=models.CASCADE)
    colonia = models.CharField('Colonia', max_length=150)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento')
    genero_id = models.ForeignKey(Genero, verbose_name='Género', on_delete=models.CASCADE)


    class Meta:
        verbose_name = "Solicitante"
        verbose_name_plural = "Solicitantes"

    def __str__(self):
        return "%i - %s" % (self.pk, self.nombre)
