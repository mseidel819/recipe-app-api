# Generated by Django 4.0.10 on 2024-01-11 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_rename_ingredient_list_blogrecipe_ingredients_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogrecipe',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='blogrecipe',
            name='instructions',
        ),
        migrations.RemoveField(
            model_name='blogrecipe',
            name='notes',
        ),
    ]