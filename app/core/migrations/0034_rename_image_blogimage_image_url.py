# Generated by Django 4.0.10 on 2024-01-11 21:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_remove_blogrecipe_image_blogimage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogimage',
            old_name='image',
            new_name='image_url',
        ),
    ]
