# Generated by Django 3.2.9 on 2022-04-01 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='medios_captacion',
            name='nomenclatura',
            field=models.CharField(default='', max_length=10, verbose_name='Nomenclatura'),
            preserve_default=False,
        ),
    ]