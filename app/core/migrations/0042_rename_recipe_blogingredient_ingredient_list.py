# Generated by Django 4.0.10 on 2024-01-14 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_blogingredientlist_alter_blogingredient_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogingredient',
            old_name='recipe',
            new_name='ingredient_list',
        ),
    ]