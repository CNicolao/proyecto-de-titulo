# Generated by Django 5.1.4 on 2024-12-08 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('STIWEBSERVICE', '0007_remove_asignacion_asignado_a_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tecnico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('disponible', models.BooleanField(default=True)),
            ],
        ),
    ]
