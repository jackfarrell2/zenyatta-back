# Generated by Django 5.1.3 on 2024-12-23 00:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('step_number', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True)),
                ('process', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='steps', to='processes.process')),
            ],
        ),
    ]