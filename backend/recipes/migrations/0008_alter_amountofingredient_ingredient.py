# Generated by Django 3.2.18 on 2023-04-12 10:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_amountofingredient_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amountofingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amount', to='recipes.ingredient', verbose_name='название ингредиента'),
        ),
    ]
