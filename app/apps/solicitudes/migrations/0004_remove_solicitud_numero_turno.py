# Generated by Django 3.2.9 on 2022-04-01 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0003_auto_20220316_1338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solicitud',
            name='numero_turno',
        ),
    ]
