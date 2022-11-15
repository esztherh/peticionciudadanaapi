# Generated by Django 3.2.9 on 2022-03-14 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status_Seguimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50, verbose_name='Estado de la Solicitud')),
                ('is_main', models.BooleanField(default=False, verbose_name='¿Es el principal?')),
                ('is_end', models.BooleanField(default=True, verbose_name='¿Es el fin?')),
                ('color', models.CharField(max_length=10, verbose_name='Color')),
                ('icono', models.CharField(max_length=100, verbose_name='Icono')),
                ('system_status', models.BooleanField(default=False, verbose_name='¿Es estatus del sistema?')),
                ('belongs_to', models.ManyToManyField(to='auth.Group', verbose_name='Canalización')),
            ],
            options={
                'verbose_name': 'Estado de Solicitud',
                'verbose_name_plural': 'Estados de las Solicitudes',
            },
        ),
    ]
