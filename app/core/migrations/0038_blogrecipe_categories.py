# Generated by Django 4.0.10 on 2024-01-12 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_remove_blogrecipe_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogrecipe',
            name='categories',
            field=models.ManyToManyField(to='core.blogcategory'),
        ),
    ]
