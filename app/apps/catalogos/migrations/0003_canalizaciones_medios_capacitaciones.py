# Generated by Django 3.2.9 on 2022-04-04 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0002_medios_captacion_nomenclatura'),
    ]

    operations = [
        migrations.AddField(
            model_name='canalizaciones',
            name='medios_capacitaciones',
            field=models.ManyToManyField(to='catalogos.Medios_Captacion'),
        ),
    ]
