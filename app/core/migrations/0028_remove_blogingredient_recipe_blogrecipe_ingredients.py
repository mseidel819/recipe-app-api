# Generated by Django 4.0.10 on 2024-01-11 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_alter_blogingredient_recipe_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogingredient',
            name='recipe',
        ),
        migrations.AddField(
            model_name='blogrecipe',
            name='ingredients',
            field=models.ManyToManyField(to='core.blogingredient'),
        ),
    ]
