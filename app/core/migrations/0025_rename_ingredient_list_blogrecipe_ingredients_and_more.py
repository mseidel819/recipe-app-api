# Generated by Django 4.0.10 on 2024-01-10 23:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_rename_ingredients_blogrecipe_ingredient_list_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogrecipe',
            old_name='ingredient_list',
            new_name='ingredients',
        ),
        migrations.AlterField(
            model_name='blogingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.blogrecipe'),
        ),
        migrations.AlterField(
            model_name='bloginstruction',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.blogrecipe'),
        ),
        migrations.AlterField(
            model_name='blognote',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.blogrecipe'),
        ),
    ]