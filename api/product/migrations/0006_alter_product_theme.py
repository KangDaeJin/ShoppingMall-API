# Generated by Django 4.0.2 on 2022-04-07 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_remove_product_stock_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.theme'),
        ),
    ]
