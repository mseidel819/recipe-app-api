# Generated by Django 4.0.10 on 2024-01-10 21:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_remove_blogingredient_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogingredient',
            name='recipe',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='core.blogrecipe'),
            preserve_default=False,
        ),
    ]