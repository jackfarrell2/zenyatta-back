# Generated by Django 5.1.3 on 2024-12-31 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processes', '0005_alter_task_process'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='description',
            new_name='content',
        ),
    ]