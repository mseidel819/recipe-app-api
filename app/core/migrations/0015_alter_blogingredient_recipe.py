# Generated by Django 4.0.10 on 2024-01-10 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_blogingredient_recipe_remove_blogrecipe_ingredients_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.blogauthor'),
        ),
    ]
