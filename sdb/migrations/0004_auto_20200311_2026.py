# Generated by Django 3.0.3 on 2020-03-11 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sdb', '0003_auto_20200311_1955'),
    ]

    operations = [
        migrations.RenameField(
            model_name='community',
            old_name='family_fk',
            new_name='conformation',
        ),
        migrations.RenameField(
            model_name='conformation',
            old_name='family_fk',
            new_name='family',
        ),
    ]
