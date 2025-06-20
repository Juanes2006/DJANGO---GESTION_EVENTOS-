# Generated by Django 5.2.1 on 2025-06-17 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('are_codigo', models.AutoField(primary_key=True, serialize=False)),
                ('are_nombre', models.CharField(max_length=45)),
                ('are_descripcion', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('cat_codigo', models.AutoField(primary_key=True, serialize=False)),
                ('cat_nombre', models.CharField(max_length=45)),
                ('cat_descripcion', models.CharField(max_length=400)),
                ('cat_area_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to='app_super_admin.area')),
            ],
        ),
    ]
