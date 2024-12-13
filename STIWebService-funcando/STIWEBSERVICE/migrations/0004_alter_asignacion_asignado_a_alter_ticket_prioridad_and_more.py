# Generated by Django 5.1.3 on 2024-12-04 05:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('STIWEBSERVICE', '0003_remove_ticket_departamento_alter_ticket_prioridad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacion',
            name='asignado_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='prioridad',
            field=models.CharField(blank=True, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')], default='Media', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='tecnico_asignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets_asignados_tecnico', to=settings.AUTH_USER_MODEL),
        ),
    ]