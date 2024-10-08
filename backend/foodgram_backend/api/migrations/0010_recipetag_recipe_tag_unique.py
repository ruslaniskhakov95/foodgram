# Generated by Django 3.2.16 on 2024-08-01 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_recipeingredient_recipe_ingr_unique'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipetag',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='recipe_tag_unique'),
        ),
    ]
