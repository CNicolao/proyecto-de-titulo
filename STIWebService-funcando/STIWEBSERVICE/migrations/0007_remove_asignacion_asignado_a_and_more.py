# Generated by Django 5.1.3 on 2024-12-04 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('STIWEBSERVICE', '0006_ticket_solucion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asignacion',
            name='asignado_a',
        ),
        migrations.RemoveField(
            model_name='asignacion',
            name='ticket',
        ),
        migrations.DeleteModel(
            name='Departamento',
        ),
        migrations.RemoveField(
            model_name='tecnico',
            name='usuario',
        ),
        migrations.DeleteModel(
            name='Asignacion',
        ),
        migrations.DeleteModel(
            name='Tecnico',
        ),
    ]
