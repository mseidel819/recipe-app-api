# Generated by Django 4.0.10 on 2024-01-11 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_remove_blogingredient_recipe_blogrecipe_ingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogrecipe',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='blogingredient',
            name='recipe',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='core.blogrecipe'),
            preserve_default=False,
        ),
    ]
