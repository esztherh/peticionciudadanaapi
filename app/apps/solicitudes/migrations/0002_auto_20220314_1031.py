# Generated by Django 3.2.9 on 2022-03-14 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('solicitantes', '0001_initial'),
        ('catalogos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('solicitudes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo_Seguimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('is_main', models.BooleanField(default=False, verbose_name='Es el seguimineto principal')),
                ('observacion', models.TextField(blank=True, null=True, verbose_name='Observacion')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grupo_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
                ('enlace_institucional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogos.canalizaciones', verbose_name='Institución a la que pertenece')),
                ('enlace_user_that_traking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enlace_user_that_traking', to=settings.AUTH_USER_MODEL, verbose_name='Usuario enlace que esta dando seguimiento')),
            ],
            options={
                'verbose_name': 'Grupo de Seguimiento',
                'verbose_name_plural': 'Grupos de Seguimientos',
            },
        ),
        migrations.CreateModel(
            name='Seguimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observaciones', models.TextField(verbose_name='Observaciones')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
                ('grupo_seguimiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.grupo_seguimiento', verbose_name='Grupo de Seguimiento')),
            ],
            options={
                'verbose_name': 'Seguimiento de Solicitud',
                'verbose_name_plural': 'Seguimiento de Soliciutudes',
            },
        ),
        migrations.CreateModel(
            name='Solicitud',
            fields=[
                ('folio', models.CharField(max_length=20, verbose_name='Folio')),
                ('numero_turno', models.CharField(max_length=20, verbose_name='No. de Turno Asignado')),
                ('asunto', models.CharField(max_length=100, verbose_name='Asunto')),
                ('fecha_solicitud', models.DateField(verbose_name='Fecha de la Solicitud')),
                ('fecha_captura', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Captura')),
                ('lugar_expedicion', models.CharField(max_length=100, verbose_name='Lugar de Expedición')),
                ('prioridad_urgente', models.BooleanField(default=False, verbose_name='Prioridad')),
                ('requiere_audiencia', models.BooleanField(default=False, verbose_name='Requiere Audiencia')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('solicitante', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='solicitantes.solicitante')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('canalizacion', models.ManyToManyField(to='catalogos.Canalizaciones', verbose_name='Canalización')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
                ('medios_captacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogos.medios_captacion', verbose_name='Medios de Captación')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.status_seguimiento', verbose_name='Estado de la Petición')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Actualizado por')),
            ],
            options={
                'verbose_name': 'Solicitud',
                'verbose_name_plural': 'Solicitudes',
                'permissions': [('list_solicitud', 'Can Lists Solicitudes'), ('view_status_enlace_solicitud', 'Can View Solicitud Enlace Status'), ('view_status_operador_solicitud', 'Can View Solicitud Operador Status'), ('view_history_solicitud', 'Can View History Solicitudes'), ('download_oficio_solicitud', 'Can Download Oficio Solicitudes'), ('export_solicitudes', 'Can Export Solicitudes')],
            },
        ),
        migrations.CreateModel(
            name='Seguimiento_Archivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='solicitud/seguimiento/archivo/', verbose_name='Archivo')),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True, verbose_name='Descripción')),
                ('solicitud_seguimiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.seguimiento', verbose_name='Seguimiento de la Solicitud')),
            ],
            options={
                'verbose_name': 'Archivo de Seguimiento',
                'verbose_name_plural': 'Archivos de Seguimientos',
            },
        ),
        migrations.CreateModel(
            name='Grupo_Seguimiento_Children',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('children_grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children_grupo', to='solicitudes.grupo_seguimiento', verbose_name='Grupo de Seguimiento Hijo')),
                ('main_grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_grupo', to='solicitudes.grupo_seguimiento', verbose_name='Grupo de Seguimiento principal')),
            ],
        ),
        migrations.AddField(
            model_name='grupo_seguimiento',
            name='solicitud',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.solicitud', verbose_name='Solicitud'),
        ),
        migrations.AddField(
            model_name='grupo_seguimiento',
            name='status_enlace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_enlace', to='solicitudes.status_seguimiento', verbose_name='Estado del Seguimiento Enlace'),
        ),
        migrations.AddField(
            model_name='grupo_seguimiento',
            name='status_operador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_operador', to='solicitudes.status_seguimiento', verbose_name='Estado del Seguimiento Operador'),
        ),
        migrations.AddField(
            model_name='grupo_seguimiento',
            name='updated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grupo_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Actualizado por'),
        ),
        migrations.CreateModel(
            name='Beneficiario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20, verbose_name='Nombre')),
                ('apellido_paterno', models.CharField(max_length=20, verbose_name='Apellido Paterno')),
                ('apellido_materno', models.CharField(max_length=20, verbose_name='Apellido Materno')),
                ('curp', models.CharField(max_length=18, verbose_name='CURP')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.solicitud', verbose_name='Solicitud')),
            ],
            options={
                'verbose_name': 'Beneficiario',
                'verbose_name_plural': 'Beneficiarios',
            },
        ),
        migrations.CreateModel(
            name='Archivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='solicitud/archivo/', verbose_name='Archivo')),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True, verbose_name='Descripción')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solicitudes.solicitud', verbose_name='Solicitud')),
            ],
            options={
                'verbose_name': 'Archivo',
                'verbose_name_plural': 'Archivos',
            },
        ),
        migrations.CreateModel(
            name='Change_Status_Seguimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('belongs_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group', verbose_name='¿Quién puede cambiarlo?')),
                ('change_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_status', to='solicitudes.status_seguimiento', verbose_name='Estado a Cambiar')),
                ('main_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_status', to='solicitudes.status_seguimiento', verbose_name='Estado')),
            ],
            options={
                'verbose_name': 'Cambio entre estado',
                'verbose_name_plural': 'Cambios entre estados',
                'unique_together': {('main_status', 'change_status', 'belongs_to')},
            },
        ),
    ]
