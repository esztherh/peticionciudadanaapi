from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import Group

from apps.catalogos.models import Medios_Captacion, Canalizaciones
from apps.solicitantes.models import Solicitante


class Status_Seguimiento(models.Model):
    status = models.CharField('Estado de la Solicitud', max_length=50)
    is_main = models.BooleanField('¿Es el principal?', default=False)
    is_end = models.BooleanField('¿Es el fin?', default=True)
    # who_can_change = models.ForeignKey(Group, verbose_name='¿Quién puede cambiarlo?', on_delete=models.CASCADE, blank=True, null=True, related_name='who_can_change')
    # belongs_to =  models.ForeignKey(Group, verbose_name='¿Quién puede cambiarlo?', on_delete=models.CASCADE, blank=True, null=True, related_name='belongs_to')
    belongs_to = models.ManyToManyField(Group, verbose_name='Canalización')
    color = models.CharField('Color', max_length=10)
    icono = models.CharField('Icono', max_length=100)
    system_status = models.BooleanField('¿Es estatus del sistema?', default=False)

    class Meta:
        verbose_name = 'Estado de Solicitud'
        verbose_name_plural = 'Estados de las Solicitudes'

    def __str__(self):
        return "%i - %s" % (self.pk, self.status)


class Change_Status_Seguimiento(models.Model):
    main_status = models.ForeignKey(Status_Seguimiento, verbose_name='Estado', on_delete=models.CASCADE, related_name='main_status')
    change_status = models.ForeignKey(Status_Seguimiento, verbose_name='Estado a Cambiar', on_delete=models.CASCADE, related_name='change_status')
    belongs_to =  models.ForeignKey(Group, verbose_name='¿Quién puede cambiarlo?', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Cambio entre estado'
        verbose_name_plural = 'Cambios entre estados'
        unique_together = (
            ("main_status", "change_status", "belongs_to"),
        )

    def __str__(self):
        return "%i - %s -> %s" % (self.pk, self.main_status.status, self.change_status.status)
        # return "%i" % (self.pk)


class Solicitud(models.Model):
    folio = models.CharField('Folio', max_length=20)
    # numero_turno = models.CharField('No. de Turno Asignado', max_length=20)
    asunto = models.CharField('Asunto', max_length=100)
    fecha_solicitud = models.DateField('Fecha de la Solicitud')
    fecha_captura = models.DateTimeField('Fecha de Captura', auto_now_add=True)
    medios_captacion = models.ForeignKey(Medios_Captacion, verbose_name='Medios de Captación', on_delete=models.CASCADE)
    # lugar_expedicion = models.CharField('Lugar de Expedición', max_length=100)
    # prioridad_urgente = models.BooleanField('Prioridad', default=False)
    canalizacion = models.ManyToManyField(Canalizaciones, verbose_name='Canalización')
    # requiere_audiencia = models.BooleanField('Requiere Audiencia', default=False)
    descripcion = models.TextField('Descripción')
    solicitante = models.OneToOneField(Solicitante, on_delete=models.CASCADE, primary_key=True)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualización', auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Creado por', on_delete=models.CASCADE, related_name='created_by')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Actualizado por', on_delete=models.CASCADE, related_name='updated_by')
    status = models.ForeignKey(Status_Seguimiento, verbose_name='Estado de la Petición', on_delete=models.CASCADE)

    nombre_servidor_publico = models.CharField('Nombre del Servidor Público', max_length=100)
    apellido_parterno_servidor_publico = models.CharField('Apellido Paterno del Servidor Público', max_length=100)
    apelliod_materno_servidor_publico = models.CharField('Apellido Materno del Servidor Público', max_length=100)
    cargo_servidor_publico = models.CharField('Cargo del Servidor Público', max_length=255)
    area_servidor_publico = models.CharField('Área del Servidor Público', max_length=255)

    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'

        permissions = [
            ('list_solicitud', 'Can Lists Solicitudes',),
            ('view_status_enlace_solicitud', 'Can View Solicitud Enlace Status',),
            ('view_status_operador_solicitud', 'Can View Solicitud Operador Status',),
            ('view_history_solicitud', 'Can View History Solicitudes',),
            ('download_oficio_solicitud', 'Can Download Oficio Solicitudes',),
            ('export_solicitudes', 'Can Export Solicitudes',),
        ]

    def __str__(self):
        return "%i - %s - %s" % (self.pk, self.numero_turno, self.asunto)


class Beneficiario(models.Model):
    nombre = models.CharField('Nombre', max_length=20)
    apellido_paterno = models.CharField('Apellido Paterno', max_length=20)
    apellido_materno = models.CharField('Apellido Materno', max_length=20)
    curp = models.CharField('CURP', max_length=18)
    solicitud = models.ForeignKey(Solicitud, verbose_name='Solicitud', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Beneficiario'
        verbose_name_plural = 'Beneficiarios'

    def __str__(self):
        return "%i - %s" % (self.pk, self.nombre)


class Archivo(models.Model):
    archivo = models.FileField("Archivo", upload_to='solicitud/archivo/', blank=True, null=True)
    descripcion = models.CharField('Descripción', max_length=100, blank=True, null=True)
    solicitud = models.ForeignKey(Solicitud, verbose_name='Solicitud', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'

    def __str__(self):
        return "%i - %s" % (self.pk, self.archivo)


class Grupo_Seguimiento(models.Model):
    solicitud = models.ForeignKey(Solicitud, verbose_name='Solicitud', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Creado por', on_delete=models.CASCADE, related_name='grupo_created_by')
    modified_at = models.DateTimeField('Fecha de Actualización', auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Actualizado por', on_delete=models.CASCADE, related_name='grupo_updated_by')
    enlace_institucional = models.ForeignKey(Canalizaciones, verbose_name='Institución a la que pertenece', on_delete=models.CASCADE)
    is_main = models.BooleanField("Es el seguimineto principal", default=False)
    observacion = models.TextField('Observacion', blank=True, null=True)
    status_enlace = models.ForeignKey(Status_Seguimiento, verbose_name='Estado del Seguimiento Enlace', on_delete=models.CASCADE, related_name='status_enlace')
    status_operador = models.ForeignKey(Status_Seguimiento, verbose_name='Estado del Seguimiento Operador', on_delete=models.CASCADE, related_name='status_operador')
    enlace_user_that_traking = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Usuario enlace que esta dando seguimiento', on_delete=models.CASCADE, related_name='enlace_user_that_traking', blank=True, null=True)

    class Meta:
        verbose_name = 'Grupo de Seguimiento'
        verbose_name_plural = 'Grupos de Seguimientos'

    def __str__(self):
        return "%i - %s | %s" % (self.pk, self.solicitud.folio, self.enlace_institucional.dependencia)


class Grupo_Seguimiento_Children(models.Model):
    main_grupo = models.ForeignKey(Grupo_Seguimiento, verbose_name='Grupo de Seguimiento principal', related_name='main_grupo', on_delete=models.CASCADE)
    children_grupo = models.ForeignKey(Grupo_Seguimiento, verbose_name='Grupo de Seguimiento Hijo', related_name='children_grupo', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)


class Seguimiento(models.Model):
    observaciones = models.TextField('Observaciones')
    grupo_seguimiento = models.ForeignKey(Grupo_Seguimiento, verbose_name='Grupo de Seguimiento', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Creado por', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Seguimiento de Solicitud'
        verbose_name_plural = 'Seguimiento de Soliciutudes'

    def __str__(self):
        return "%i - %s" % (self.pk, self.observaciones)


class Seguimiento_Archivo(models.Model):
    archivo = models.FileField("Archivo", upload_to='solicitud/seguimiento/archivo/', blank=True, null=True)
    descripcion = models.CharField('Descripción', max_length=100, blank=True, null=True)
    solicitud_seguimiento = models.ForeignKey(Seguimiento, verbose_name='Seguimiento de la Solicitud', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Archivo de Seguimiento'
        verbose_name_plural = 'Archivos de Seguimientos'

    def __str__(self):
        return "%i - %s" % (self.pk, self.archivo)
