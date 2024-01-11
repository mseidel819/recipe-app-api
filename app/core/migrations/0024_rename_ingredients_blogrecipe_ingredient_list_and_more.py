# Generated by Django 4.0.10 on 2024-01-10 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_blogrecipe_author'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogrecipe',
            old_name='ingredients',
            new_name='ingredient_list',
        ),
        migrations.AlterField(
            model_name='blogingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='core.blogrecipe'),
        ),
    ]
